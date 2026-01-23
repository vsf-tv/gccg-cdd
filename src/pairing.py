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
# Standard library imports
import time
from typing import Optional

# Generated model imports
from internal_api_client.api.default_api import DefaultApi
from internal_api_client.api_client import ApiClient
from internal_api_client.configuration import Configuration
from internal_api_client.exceptions import ApiException
from internal_api_client.models.authenticate_response_content import AuthStatus
from internal_api_client.models.authenticate_request_content import AuthenticateRequestContent
from internal_api_client.models.authenticate_response_content import AuthenticateResponseContent
from internal_api_client.models.pair_request_content import PairRequestContent
from internal_api_client.models.pair_failure_reason import PairFailureReason
from internal_api_client.models.pair_response_content import PairResponseContent
from internal_api_client.models.protocol_version import ProtocolVersion
from internal_api_client.models.success import Success

# Local application imports
from credentialstore import CredentialStore
from custom_exceptions import (
    PairingError,
    PairingServiceRequestConnectionError,
    PairingServiceRequestTimeoutError,
    PairingServiceResponseError,
    PairingCompatibilityVersionError,
    PairingCompatibilityDeviceTypeError,
    PairingCompatibilityHostIDError
)
from custom_logger import logger

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

        # Create separate API clients for pair and authenticate endpoints
        pair_config = Configuration(host=pairing_url)
        self.pair_api_client = ApiClient(configuration=pair_config)
        self.pair_api = DefaultApi(api_client=self.pair_api_client)
        
        auth_config = Configuration(host=auth_url)
        self.auth_api_client = ApiClient(configuration=auth_config)
        self.auth_api = DefaultApi(api_client=self.auth_api_client)

        # These values will be set by get_new_pairing_code().
        self.pair_response: Optional[PairResponseContent] = None
        self.auth_response: Optional[AuthenticateResponseContent] = None

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
        if diff > self._get_success_data().pairing_timeout_seconds:
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
            0, self._get_success_data().pairing_timeout_seconds - (now - self.start_time)
        )

    def get_new_pairing_code(self):
        try:
            # Grab the TR12 version from the generated client
            version: str = ProtocolVersion().version
            logger.info(f"Using Protocol Version: {version}")
            self.certs.generate_keys_and_csr()
            pair_request = PairRequestContent.from_dict({
                "deviceType": self.device_type,
                "hostId": self.host_id,
                "csr": self.certs.csr,
                "version": version
            })
            
            logger.info(f"Calling pair API with base URL: {self.pairing_url}")
            # Pydantic nested validation bug requires using to_dict() method for nested objects
            self.pair_response: Optional[PairResponseContent]= self.pair_api.pair(
                pair_request_content=pair_request.to_dict(),
                _request_timeout=MAX_TIMEOUT_SEC
            )

        except ApiException as e:
            logger.error(f"API Exception - Status: {e.status}, Body: {e.body}, Reason: {e.reason}")
            raise PairingError(
                details=f"API Error - StatusCode: {e.status} - Response: {e.body}"
            )
        except TimeoutError as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except Exception as e:
            logger.error(f"Unexpected exception in get_new_pairing_code: {type(e).__name__}: {e}")
            raise PairingError(details=f"Msg: {e}")
        
        # assuming the request succeeded, the client/host compatibility might have failed
        result = self.pair_response.result
        if isinstance(result.actual_instance, Success):
            # success - actual_instance is Success wrapper, .success is PairSuccessData
            return True
        else:
            # actual_instance is Failure wrapper, .failure is PairFailureData
            failure_data = result.actual_instance.failure
            if failure_data.reason == PairFailureReason.VERSION_NOT_SUPPORTED:
                raise PairingCompatibilityVersionError(
                    details=f"Pairing Failed: {failure_data.reason}"
                )

            if failure_data.reason == PairFailureReason.DEVICE_TYPE_NOT_SUPPORTED:
                raise PairingCompatibilityDeviceTypeError(
                    details=f"Pairing Failed: {failure_data.reason}"
                )

            if failure_data.reason == PairFailureReason.HOST_ID_MISMATCH:
                raise PairingCompatibilityHostIDError(
                    details=f"Pairing Failed: {failure_data.reason}"
                )

            raise PairingError()

    def _get_success_data(self):
        """Helper to get the success data from the pair response union.
        actual_instance is Success wrapper, .success is PairSuccessData"""
        return self.pair_response.result.actual_instance.success

    def get_pairing_code(self) -> str:
        """
        Returns the pairing code if available, otherwise returns an empty string.

        Returns:
           str: The pairing code if available, otherwise an empty string.
        """
        if self.pair_response:
            return self._get_success_data().pairing_code
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
            auth_request = AuthenticateRequestContent.from_dict({
                "deviceId": self._get_success_data().device_id,
                "pairingCode": self._get_success_data().pairing_code,
                "accessCode": self._get_success_data().access_code,
            })

            # Pydantic nested validation bug requires using to_dict() method for nested objects
            self.auth_response: AuthenticateResponseContent = self.auth_api.authenticate(
                authenticate_request_content=auth_request.to_dict(),
                _request_timeout=MAX_TIMEOUT_SEC
            )

        except ApiException as e:
            raise PairingError(
                details=f"API Error - StatusCode: {e.status} - Response: {e.body}"
            )
        except TimeoutError as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except Exception as e:
            raise PairingError(details=f"Msg: {e}")

        # The pairing code has not yet been claimed.
        if self.auth_response.status == AuthStatus.STANDBY :
            logger.info(f"Waiting for Authorization on: {self._get_success_data().pairing_code}")
            return False

        # The pairing code has been claimed.
        elif self.auth_response.status == AuthStatus.CLAIMED:
            logger.info(f"Authenticated!:  Auth response: {self.auth_response}")
            try:
                self.certs.write_to_filesystem(
                    device_id=self._get_success_data().device_id,
                    auth_response=self.auth_response
                )
                return True
            except Exception as e:
                raise PairingError(details=f"Unable to write certs to disk: {e}")
        else:
            raise PairingServiceResponseError(details=f"Unexpected status")
