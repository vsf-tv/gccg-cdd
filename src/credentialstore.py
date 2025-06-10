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

import attr
import cattr
from topics import Topics
import os
from pathlib import Path
import shutil
from threading import Lock
from typing import Union, Optional
from custom_exceptions import (
    CertificatesInvalid,
    CertificatesWriteError,
    CertificatesReadError,
    SystemIntegrationError,
    DeprovisionError
)
from utils import generate_csr, generate_client_keys

from service_api_models import (
    HostSettings,
    PairResponse,
    AuthResponse,
    ConnectionSettings
)


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

        # self.device_id_file: str = os.path.join(self.dir, "device_id")
        self.ca_cert_file: str = os.path.join(self.dir, "ca_cert")
        self.device_cert_file: str = os.path.join(self.dir, "device_cert")
        self.priv_key_file: str = os.path.join(self.dir, "priv_key")
        self.host_settings_file: str = os.path.join(self.dir, "host_settings")
        self.host_settings: Union[HostSettings, None] = None
        self.connection_settings_file: str = os.path.join(self.dir, "connection_settings")
        self.connection_settings: Optional[ConnectionSettings] = None
        self.uri: str = ""
        self.region: str = ""
        self.device_id: str = ""
        self._topics = None
        self.pub_key: str = ""
        self.priv_key: str = ""
        self.csr: str = ""
        self.read_write_lock = Lock()

    def get_topics(self) -> Union[Topics, None]:
        """
        Returns the topics object for this device when the device_id is known.

        Returns:
            Union[Topics, None]   None when certs aren't initialized with a device_id.
        """
        return self._topics

    def generate_keys_and_csr(self):
        """
        Generate keys and CSR for the device.
        Service will be given the pub_key and Certificate Signing Request (CSR) in order to
        generate device_cert for the MQTT connection.
        """
        if not self.csr:
            print("Generating keys and CSR")
            self.pub_key, self.priv_key = generate_client_keys()
            self.csr = generate_csr(self.priv_key)
        else:
            # No need to re-generate.
            print("Keys and CSR already generated")

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
            print(f"Check if device has certs file: {self.dir}")

            if not os.path.exists(self.dir):
                # This is normal if the device has never paired.
                print(f"Missing: certs directory, not paired yet: {self.dir}")
                return False

            if not os.path.exists(self.ca_cert_file):
                print(f"Missing ca_cert_file file, not paired yet: {self.ca_cert_file}")
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
                    self.connection_settings = cattr.structure(json.loads(f.read()), ConnectionSettings)

                    self.device_id = self.connection_settings.device_id
                    self.uri = self.connection_settings.uri
                    self.region = self.connection_settings.region

            except Exception as e:
                # file system error or some kind of permissions problem.
                raise CertificatesReadError(
                    details=f"Invalid connection_settings file: {self.connection_settings_file}.  Deregister and re-pair the device"
                ) from e

            try:
                with open(self.host_settings_file, "r") as f:
                    self.host_settings = cattr.structure_attrs_fromdict(json.load(f), HostSettings)
            except Exception as e:
                # File system error or some kind of permissions problem.
                raise CertificatesReadError(
                    details=f"Invalid host_settings: {self.host_settings_file}. Re-pair device. Msg: {e}."
                ) from e

            # Topics are typically device_id dependent in a host service for message routing
            # and IAM controls.
            self._topics = Topics(self.device_id, self.host_settings)

            # Cert files exists, initialized and ready to use.
            return True

    def write_to_filesystem(
            self,
            pair_response: PairResponse,
            auth_response: AuthResponse
    ):
        """
        Saves certs and host_settings to the file system.
        The cert path on the filesystem was verified as writable on SDK start but if that subsequently changed,
        then an exception is raised here on failure to write.

        Args:
           PairResponse, AuthResponse:  See Host Service API

        Returns:
            None

        Raises:
            CertificatesWriteError (See custom_exceptions)
            CertificatesInvalid
        """
        self.device_id = pair_response.device_id
        with self.read_write_lock:
            print("writing certs to file")
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
                    # Write the UriModel to both validate and write to file.
                    self.connection_settings = ConnectionSettings(
                        device_id=pair_response.device_id,
                        uri=auth_response.MQTTUri,
                        region=auth_response.region
                    )
                    f.write(json.dumps(cattr.unstructure(self.connection_settings)))

                with open(self.host_settings_file, "w") as f:
                    json.dump(cattr.unstructure(pair_response.host_settings), f)

            except Exception as e:
                # File system Error or some kind of permissions problem that changed after the SDK was started.
                raise CertificatesWriteError(
                    details=f"Unable to write certificates to the device: {e}."
                )

            self._topics = Topics(self.device_id, pair_response.host_settings)

    def update_device_cert_file(self, device_cert: str):
        """
        Updates the device cert file on the filesystem.
        Args:  device_cert PEM str format.
        """
        assert device_cert, "Device_cert is required."
        with open(self.device_cert_file, "w") as f:
            print(f"Updating device cert file: {self.device_cert_file}.")
            f.write(device_cert)

    def deprovision(self):
        """
        Deprovision the device by removing the certs from the filesystem.
        """
        print(f"Called deprovision.")
        try:
            shutil.rmtree(self.dir)
        except Exception as e:
            raise DeprovisionError(details=f"Unable to deprovision: {e}.")
