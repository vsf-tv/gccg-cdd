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
import json
import os
import shutil
from pathlib import Path
from threading import Lock
from typing import Optional, Union

# Third-party imports
import cattr

# Generated model imports
from internal_api_client.models.authenticate_response_content import AuthenticateResponseContent
from internal_api_client.models.host_settings import HostSettings
from internal_api_client.models.rotate_certificates_request_content import RotateCertificatesRequestContent

# Local application imports
from cdd_internal_models import ConnectionSettings
from custom_exceptions import (
    CertificatesReadError,
    CertificatesWriteError,
    DeprovisionError,
    SystemIntegrationError,
    ConnectError
)
from custom_logger import logger
from utils import generate_client_keys, generate_csr


class CredentialStore(object):
    """
    Persists identity, certs and host settings on the filesystem.
    Creates certs in: base/device_local_id/<host_id>.
    SDK must have read/write access to the <base> folder.
    Filesystem should be persistent to preserve certs and enable automatic (re)connect on restart.

    Attributes:
        base (str): Root directory path where certs will be placed.
        device_local_id (str): Client provided UUID for this device where certs are persisted.

    Raises:
        SystemIntegrationError (see custom_exceptions).
    """

    def __init__(self, base: str, device_local_id: str, host_id: str):
        self.device_local_id = device_local_id
        self.base = base
        try:
            # Certs <certs_path (provided on SDK start)>/<device_local_id>/host_id/.
            self.dir: str = os.path.join(self.base, self.device_local_id, host_id)
            Path(self.dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Writable folder is already checked in the SDK constructor, should not happen.
            raise SystemIntegrationError(
                details=f"Certs directory is not writable: {self.base}"
            )

        self.ca_cert_file: str = os.path.join(self.dir, "ca_cert")
        self.device_cert_file: str = os.path.join(self.dir, "device_cert")
        self.priv_key_file: str = os.path.join(self.dir, "priv_key")
        self.host_settings_file: str = os.path.join(self.dir, "host_settings")
        self.host_settings: Union[HostSettings, None] = None
        self.connection_settings_file: str = os.path.join(self.dir, "connection_settings")
        self.connection_settings: Optional[ConnectionSettings] = None
        self.priv_key: str = ""  # need to keep between pair() and auth()
        self.pub_key: str = ""  # need to keep between pair() and auth()
        self.csr: str = ""  # need to keep between pair() and auth()
        self.read_write_lock = Lock()

    def get_device_id(self) -> str:
        return self.connection_settings.device_id

    def get_uri(self) -> str:
        return self.connection_settings.uri

    def get_region(self) -> str:
        return self.connection_settings.region

    def get_connected_host_settings(self) -> HostSettings:
        if not self.host_settings:
            raise ConnectError(details="Host settings not initialized.  Likely not connected.")
        return self.host_settings

    def generate_keys_and_csr(self):
        """
        Generate keys and Certificate Singing Request (CSR) needed for the service to
        generate a device_cert for the MQTT connection.
        """
        if not self.csr:
            logger.info("Generating keys and CSR")
            self.pub_key, self.priv_key = generate_client_keys()
            self.csr = generate_csr(self.priv_key)
        else:
            # No need to re-generate.
            logger.info("Keys and CSR already generated")

    def read_from_filesystem(self) -> bool:
        """
        Returns:
            True: the certs are available and if current will enable connect().
            False:the certs have not been stored previously as the device isn't yet claimed.

        Raises:
            CertificatesReadError (See custom_exceptions)
            CertificatesInvalid
        """
        with self.read_write_lock:
            logger.info(f"Check if device has certs file: {self.dir}")

            if not os.path.exists(self.dir):
                # This is normal if the device has never paired.
                logger.info(f"Missing: certs directory, not paired yet: {self.dir}")
                return False

            if not os.path.exists(self.ca_cert_file):
                logger.info(f"Missing ca_cert_file file, not paired yet: {self.ca_cert_file}")
                return False

            # At this point, Certs should ALL be available. Fatal otherwise.
            # Possibly: file system space issue or the SDK died or device shut down while pairing.
            for file in [
                self.ca_cert_file,
                self.device_cert_file,
                self.priv_key_file,
                self.connection_settings_file,
                self.host_settings_file,
            ]:
                if not os.path.exists(file):
                    raise CertificatesReadError(
                        details=f"Missing: {file}. Should deregister and re-pair the device."
                    )
            try:
                with open(self.connection_settings_file, "r") as f:
                    self.connection_settings = cattr.structure(json.load(f), ConnectionSettings)

            except Exception as e:
                # file system error or some kind of permissions problem.
                raise CertificatesReadError(
                    details=(
                        f"Invalid connection_settings file: {self.connection_settings_file}. "
                        "Deregister and re-pair the device."
                    )
                ) from e

            try:
                with open(self.host_settings_file, "r") as f:
                    self.host_settings = HostSettings.from_dict(json.load(f))
            except Exception as e:
                # File system error or some kind of permissions problem.
                raise CertificatesReadError(
                    details=f"Invalid host_settings: {self.host_settings_file}. Re-pair device. Msg: {e}."
                ) from e

            # Cert files exists, initialized and ready to use.
            return True

    def write_to_filesystem(
            self,
            device_id: str,
            auth_response: AuthenticateResponseContent
    ):
        """
        Saves certs and host_settings to the file system.
        The cert path on the filesystem was verified as writable on SDK start but if that subsequently changed,
        then an exception is raised here on failure to write.

        Args:
           device_id: Device ID from successful pair response
           auth_response: AuthResponse from Host Service API

        Returns:
            None

        Raises:
            CertificatesWriteError (See custom_exceptions)
            CertificatesInvalid
        """
        with self.read_write_lock:
            logger.info("writing certs to file")
            try:
                # This has already been validated to exist.
                if not os.path.exists(self.dir):
                    os.mkdir(self.dir)

                with open(self.ca_cert_file, "w") as f:
                    f.write(auth_response.ca_cert)

                with open(self.device_cert_file, "w") as f:
                    f.write(auth_response.device_cert)

                with open(self.priv_key_file, "w") as f:
                    f.write(self.priv_key)

                with open(self.connection_settings_file, "w") as f:
                    self.connection_settings = ConnectionSettings(
                        device_id=device_id,
                        uri=auth_response.mqtt_uri,
                        region=auth_response.region
                    )
                    f.write(json.dumps(cattr.unstructure(self.connection_settings)))

                with open(self.host_settings_file, "w") as f:
                    json.dump(auth_response.host_settings.to_dict(), f)

            except Exception as e:
                # File system Error or some kind of permissions problem that changed after the SDK was started.
                self.deprovision()
                raise CertificatesWriteError(
                    details=f"Unable to write certificates to the device: {e}."
                )

    def rotate_certs(self, certs_rotate: RotateCertificatesRequestContent) -> bool:
        """
        Updates the device cert and connection settings file on the filesystem.
        If an update is needed, then return True

        Args:  device_cert PEM str format.
        """
        need_to_update: bool = False

        # Update a changed device cert persisted in the device_cert_file.
        with open(self.device_cert_file, "r") as file:
            current_cert_pem_str = file.read()
            if certs_rotate.device_cert != current_cert_pem_str:
                logger.info("Updating device credentials")
                with open(self.device_cert_file, "w") as f:
                    f.write(certs_rotate.device_cert)
                need_to_update = True

        # Update a changed MQTT Uri or Region description persisted in the connection_settings file.
        if (certs_rotate.mqtt_uri != self.connection_settings.uri or
                certs_rotate.region != self.connection_settings.region):
            with open(self.connection_settings_file, "w") as f:
                self.connection_settings = ConnectionSettings(
                    device_id=self.connection_settings.device_id,
                    uri=certs_rotate.mqtt_uri,
                    region=certs_rotate.region
                )
                f.write(json.dumps(cattr.unstructure(self.connection_settings)))
                need_to_update = True

        return need_to_update

    def deprovision(self):
        """
        Deprovision the device by removing the certs from the filesystem.
        """
        print(f"Removing certs from device for: {self.dir}")
        try:
            shutil.rmtree(self.dir)
        except Exception as e:
            raise DeprovisionError(details=f"Unable to deprovision: {e}.")
