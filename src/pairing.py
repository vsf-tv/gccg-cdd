# Copyright 2025 Amazon.com Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import cattr
import requests
import time
from typing import Optional
from credentialstore import CredentialStore
from custom_exceptions import (
    PairingError,
    PairingServiceRequestConnectionError,
    PairingServiceRequestTimeoutError,
    PairingServiceResponseError,
)
from custom_logger import logger
from service_api_models import HostSettings, PairRequest, PairResponse, AuthRequest, AuthResponse

MAX_TIMEOUT_SEC = 5


class Pairing(object):
    """
    Manages the pairing process. Handles calls to get pairing code and authenticate
    Update Certs accordingly.

    Args:
       certs (CredentialStore): Certs class that will be updated on successful pairing.
    """

    def __init__(
        self, certs: CredentialStore, device_type: str, host_id: str, pairing_url: str, auth_url: str
    ):
        self.certs = certs
        self.device_type = device_type
        self.host_id = host_id
        self.expired = False
        self.start_time = int(time.time())
        self.pairing_url = pairing_url
        self.auth_url = auth_url

        # These values will be set by get_new_pairing_code().
        self.pair_response: Optional[PairResponse] = None
        self.auth_response: Optional[AuthResponse] = None

    def is_expired(self):
        """
        Has the pairing process timed out according to the HostConfiguration PAIRING_TIMEOUT_SECONDS.

        Args: None

        Returns:
            bool: True if expired
        """
        if not self.pair_response:
            return False

        now = int(time.time())
        diff = now - self.start_time
        if diff > self.pair_response.pairing_timeout_seconds:
            logger.info(f"Pairing Expired.")
            return True
        return False

    def expires_in(self) -> int:
        """
        Time in seconds until the current pairing process will time out
        according to the HostConfiguration PAIRING_TIMEOUT_SECONDS.

        Args: None

        Returns:
            <int>: seconds >= 0
        """
        if not self.pair_response:
            return 0
        now = int(time.time())
        return max(
            0, self.pair_response.pairing_timeout_seconds - (now - self.start_time)
        )

    def get_new_pairing_code(self):
        try:
            self.certs.generate_keys_and_csr()
            pair_request: PairRequest = PairRequest(
                device_type=self.device_type,
                host_id=self.host_id,
                csr=self.certs.csr,
            )
            with requests.post(
                    self.pairing_url,
                    json=cattr.unstructure(pair_request),
                    timeout=MAX_TIMEOUT_SEC,
            ) as response:
                logger.info(f"Pairing response: {response.text}")

                # Check status code first
                if response.status_code != 200:
                    raise PairingError(
                        details=f"StatusCode: {response.status_code} - Response: {response.text}"
                    )

                response_json = json.loads(response.text)

        except requests.HTTPError as e:
            # This is now redundant but kept for defensive programming
            raise PairingError(
                details=f"HTTP Error - StatusCode: {response.status_code} - Msg: {e}"
            )
        except requests.ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except requests.Timeout as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except json.JSONDecodeError as e:
            raise PairingServiceResponseError(details=str(e.msg))
        except Exception as e:
            raise PairingError(details=f"Msg: {e}")

        try:
            # Parse the response. Let the PairResponse class handle validation.
            self.pair_response = cattr.structure(response_json, PairResponse)
        except Exception as e:
            raise PairingServiceResponseError(details=f"Msg: {e}")

        return True

    def get_pairing_code(self) -> str:
        """
        Returns the pairing code if available, otherwise returns an empty string.

        Returns:
           str: The pairing code if available, otherwise an empty string.
        """
        if self.pair_response:
            return self.pair_response.pairing_code
        return ""

    def authenticate_pairing_code(self) -> bool:
        """
        Authenticates the pairing code with the remote service.
        If the response indicates the client was claimed and contains credentials, then write them to disk.

        Returns:
           bool: True if authentication is successful, False otherwise.

        Raises:
           PairingError: When the authentication service returns status_code != 200.
           PairingServiceConnectionError: (see custom_exceptions)
           PairingServiceResponseError:
        """
        if not self.pair_response:
            raise PairingError(details="No pairing code to authenticate")

        # Call the Host Service Auth API.
        try:
            # Host Service API auth request model.
            auth_request: AuthRequest = AuthRequest(
                device_id=self.pair_response.device_id,
                pairing_code=self.pair_response.pairing_code,
                access_code=self.pair_response.access_code,
            )
            with requests.post(
                    self.auth_url,
                    json=cattr.unstructure(auth_request),
                    timeout=MAX_TIMEOUT_SEC,
            ) as response:

                # Check status code first
                if response.status_code != 200:
                    raise PairingError(
                        details=f"StatusCode: {response.status_code} - Response: {response.text}"
                    )

                response_json = json.loads(response.text)

        except requests.HTTPError as e:
            # This is now redundant but kept for defensive programming
            raise PairingError(
                details=f"HTTP Error - StatusCode: {response.status_code} - Msg: {e}"
            )
        except requests.ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except requests.Timeout as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except json.JSONDecodeError as e:
            raise PairingServiceResponseError(details=str(e.msg))
        except Exception as e:
            raise PairingError(details=f"Msg: {e}")

        try:
            # Parse the response. Let the AuthResponse class handle validation.
            self.auth_response = cattr.structure(response_json, AuthResponse)
        except Exception as e:
            raise PairingServiceResponseError(details=f"Msg: {e}")

        # The service response MUST include either of the following:
        if self.auth_response.status == "STANDBY":
            # OK the API responded with something valid.
            # Auth on the pairing code not complete or pairing/access codes are expired, never existed.
            logger.info(f"Waiting for Authorization on: {self.pair_response.pairing_code}")
            return False

        elif self.auth_response.status == "CLAIMED":
            logger.info("Authenticated!")
            try:
                self.certs.write_to_filesystem(
                    pair_response=self.pair_response,
                    auth_response=self.auth_response
                )
                return True
            except Exception as e:
                raise PairingError(details=f"Unable to write certs to disk: {e}")
        else:
            raise PairingServiceResponseError(details=f"Response: {response_json}")
