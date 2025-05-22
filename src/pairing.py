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
from host_settings import HostSettings

MAX_TIMEOUT_SEC = 5


class Pairing(object):
    """
    Manages the pairing process. Handles calls to get pairing code and authenticate
    Update Certs accordingly.

    Args:
       certs (CredentialStore): Certs class that will be updated on successful pairing.
    """

    def __init__(
        self, certs: CredentialStore, device_type: str, pairing_url: str, auth_url: str
    ):
        self.certs = certs
        self.device_type = device_type
        self.has_pairing_code = False
        self.expired = False
        self.start_time = int(time.time())
        self.pairing_url = pairing_url
        self.auth_url = auth_url

        # These values will be set by get_new_pairing_code().
        self.device_id: str = ""
        self.pairing_code: str = ""
        self.access_code: str = ""
        self.host_settings: Optional[HostSettings] = None

        # This value will be set by authenticate_pairing_code().
        self.certs_payload = {}

    def is_expired(self):
        """
        Has the pairing process timed out according to the HostConfiguration PAIRING_TIMEOUT_SECONDS.

        Args: None

        Returns:
            bool: True if expired
        """
        if not self.host_settings:
            return False

        now = int(time.time())
        diff = now - self.start_time
        print(f"Time now {now}. Started at: {self.start_time}. In {diff} seconds.")
        if diff > self.host_settings.pairing_timeout_seconds:
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
        if not self.host_settings:
            return 0
        now = int(time.time())
        return max(
            0, self.host_settings.pairing_timeout_seconds - (now - self.start_time)
        )

    def get_new_pairing_code(self):
        """
        Populates the instance with freshly obtained pairing codes.

        Args: None

        Returns: None

        Raises:
           PairingError: When the authentication service returns status_code != 200.
           PairingServiceConnectionError: (see custom_exceptions)
           PairingServiceResponseError: (see custom_exceptions)

        """
        self.has_pairing_code = False

        # Call the Pair Host Service API.
        rjson = self.pair()

        # Validate the payload.
        device_id = rjson.get("device_id", "")
        pairing_code = rjson.get("pairing_code", "")
        access_code = rjson.get("access_code", "")
        host_settings_json = rjson.get("host_settings", {})

        if not device_id:
            raise PairingServiceResponseError(details="Missing: device_id")

        if not pairing_code:
            raise PairingServiceResponseError(details="Missing: pairing_code")

        if not access_code:
            raise PairingServiceResponseError(details="Missing access_code")

        if not host_settings_json:
            raise PairingServiceResponseError(details="Missing host_settings")

        # OK response.
        print(f"Pairing Response: pairing code: {pairing_code}   device_id: {device_id} "
              f"host_settings: {host_settings_json}")
        try:
            self.device_id = device_id
            self.pairing_code = pairing_code
            self.access_code = access_code
            self.host_settings = cattr.structure(host_settings_json, HostSettings)
            self.has_pairing_code = True
        except (TypeError, ValueError, AttributeError) as e:
            raise PairingServiceResponseError(details=f"Pairing: Invalid HostSettings payload. Msg: {e}") from e
        except Exception as e:
            raise PairingError(details=f"Pairing: Unknown error. Msg: {e}")

    def pair(self):
        try:
            with requests.get(
                    self.pairing_url,
                    params={"device_type": self.device_type},  # Sets a query string param.
                    timeout=MAX_TIMEOUT_SEC,
            ) as response:
                print(f"Pairing response: {response.text}")
                return json.loads(response.text)

        except requests.HTTPError as e:
            if 200 != response.status_code:
                raise PairingError(
                    details=f"StatusCode: {response.status_code} - Msg: {e}"
                )
        except requests.ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except requests.Timeout as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except json.JSONDecodeError as e:
            raise PairingServiceResponseError(details=str(e.msg))
        except Exception as e:
            raise PairingError(details=f"Msg: {e}")

    def authenticate_pairing_code(self) -> bool:
        """
        Authenticates the pairing code with the remote service.
        If found, write certs to disk.
        This generates a public/private keypair and certificate signing request (csr)
        Certs generated by service will utilize these to generate the device cert.

        Returns:
           bool: True if authentication is successful, False otherwise.

        Raises:
           PairingError: When the authentication service returns status_code != 200.
           PairingServiceConnectionError: (see custom_exceptions)
           PairingServiceResponseError:
        """
        if not self.has_pairing_code:
            raise PairingError(details="No pairing code to authenticate")

        # Call the Host Service Auth API.
        rjson: dict = self.auth()

        status = rjson.get("status", "")

        # The service response MUST include either of the following:
        if status == "STANDBY":
            # OK the API responded with something valid.
            # Auth on the pairing code not complete or pairing/access codes are expired, never existed.
            print(f"Waiting for Authorization on: {self.pairing_code}")
            return False

        elif status == "CLAIMED":
            print("Authenticated!")
            try:
                self.certs.write_to_filesystem(
                    ca_cert=rjson.get("ca_cert"),
                    device_cert=rjson.get("device_cert"),
                    uri=rjson.get("MQTTUri"),
                    host_settings=self.host_settings,
                )
                return True
            except Exception as e:
                raise PairingError(details=f"Unable to write certs to disk: {e}")
        else:
            raise PairingServiceResponseError(details=f"Response: {rjson}")

    def auth(self):
        try:
            self.certs.generate_keys_and_csr(device_id=self.device_id)

            with requests.post(
                    self.auth_url,
                    json={
                        "device_id": self.device_id,
                        "pairing_code": self.pairing_code,
                        "access_code": self.access_code,
                        "public_key": self.certs.pub_key,
                        "csr": self.certs.csr,
                    },
                    timeout=MAX_TIMEOUT_SEC,
            ) as response:
                return json.loads(response.text)

        except requests.HTTPError as e:
            if 200 != response.status_code:
                raise PairingError(
                    details=f"StatusCode: {response.status_code} - Msg: {e}"
                )
        except requests.ConnectionError as e:
            raise PairingServiceRequestConnectionError(details=f"Msg: {e}")
        except requests.Timeout as e:
            raise PairingServiceRequestTimeoutError(details=f"Msg: {e}")
        except json.JSONDecodeError as e:
            raise PairingServiceResponseError(details=str(e.msg))
        except Exception as e:
            raise PairingError(details=f"Msg: {e}")
