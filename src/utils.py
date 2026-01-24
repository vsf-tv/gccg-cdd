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
from dataclasses import dataclass
import os
import json
import requests
import random
import string
import time
import ssl
import paho.mqtt.client as mqtt
from collections import deque
from custom_exceptions import MQTTPublishError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from custom_exceptions import SystemIntegrationError, UploadError
from custom_logger import logger
from internal_api_client.models.get_host_config_response_content import GetHostConfigResponseContent

# Simple UUID for the subscribed configuration update ID.
UPDATE_ID_SIZE = 5

def publish_message(client, topic: str, payload: str, qos: int, retain: bool):
    """
    Publish a message to the MQTT broker.

    Raises:
        ReportStatusError: For all MQTT publish error codes.

    """
    try:
        result, mid = client.publish(topic, payload, qos=qos, retain=retain)
    except Exception as e:
        raise MQTTPublishError(details=f"MQTT publish error.Msg: {e}") from e

    if result == mqtt.MQTT_ERR_SUCCESS:
        logger.info(f"Message {mid} accepted for delivery")
        return

    raise MQTTPublishError(details=f"MQTT publish error. Response Code: {result}")


@dataclass
class UpdateID(object):
    base = "".join(random.choices(string.ascii_letters, k=UPDATE_ID_SIZE))
    sequence = 0

    def get(self):
        self.sequence += 1
        return f"{self.base}_{self.sequence}"


class Throttle(object):
    """
    Rate limit status updates. The host service will have throttling enforcement that might
    disconnect or revoke a device if it is publishing too frequently. This SDK enforces a minimum
    time to prevent this.

    Maintains a 10s time window so short bursts are somewhat tolerated.

    For mub_min_interval = 2 and a 10-second trailing window: max 5 pubs are allowed and on average no more than
    1 pub every 2 seconds.  Burst of 5 pubs within a 10s window are still tolerated.

    """
    def __init__(self, pub_min_interval: int = 1, window_seconds: int = 10):
        self.max_publish_in_window: int = max(int(window_seconds / max(pub_min_interval, 1)), 5)
        self.window = window_seconds
        self.publish_times = deque()

    def can_publish(self) -> bool:
        now = int(time.time())
        cutoff = now - self.window
        
        # Remove expired timestamps from the left (oldest)
        while self.publish_times and self.publish_times[0] <= cutoff:
            self.publish_times.popleft()
        
        if len(self.publish_times) >= self.max_publish_in_window:
            return False
        
        self.publish_times.append(now)
        return True


def validate_path_exists_and_writeable(path: str):

    if not os.path.exists(path):
        raise IOError(f"The path {path} does not exist")
    elif not os.path.isdir(path):
        raise IOError(f"The path {path} is not a directory")
    else:
        try:
            test_file = os.path.join(path, ".write_test")
            with open(test_file, "w") as f:
                f.write("")
            os.remove(test_file)
            logger.info(f"The directory {path} is writable")
        except Exception as e:
            raise PermissionError(f"The directory {path} is not writable: {str(e)}")


def ssl_alpn(ca_cert, device_cert, private_key, iot_protocol_name):
    """
    This function populates an ssl objected consumed by the MQTT client to properly configure the network protocol.

    Args:
        ca_cert (root ca cert):
        device_cert (device_certificate)
        private_key (device private key in the pub/priv pair used in the auth process)
        iot_protocol_name (provided by the service in the HostSettings payload)
    Raises:
        Exception: For unknown errors accessing ssl primitives.
    """
    try:
        logger.info(f"open ssl version:{format(ssl.OPENSSL_VERSION)}")
        ssl_context = ssl.create_default_context()
        ssl_context.set_alpn_protocols([iot_protocol_name])
        ssl_context.load_verify_locations(cafile=ca_cert)
        ssl_context.load_cert_chain(certfile=device_cert, keyfile=private_key)
        return ssl_context
    except Exception as e:
        raise Exception(f"Failed to setup SSL. Msg:{e}")


def generate_client_keys() -> (str, str):
    """
    Generate a public/private key pair for the device.

    Args: None

    Returns:
        public_pem (str): The public key in PEM format
        private_pem (str): The private key in PEM format
    Raises:
        Exception: For unknown errors accessing ssl primitives.
    """
    logger.info("Generating key pair")
    # Generate private key.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Generate public key.
    public_key = private_key.public_key()

    # Serialize private key - store securely.
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')

    # Serialize public key - this will be sent to host service.
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')

    return public_pem, private_pem


# Generate CSR using the key pair.
def generate_csr(private_key_pem: str) -> str:
    """
    Generate a Certificate Signing Request (CSR).

    Args:
        private_key_pem: private key in PEM format

    Returns:
        csr: Certificate Signing Request str in PEM format

    """
    logger.info(f"Generating CSR")
    private_key_b = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VSF-CDD"),
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                ]
            )
        )
        .sign(private_key_b, hashes.SHA256())
    )

    return csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')


def get_host_configuration(host_id: str) -> GetHostConfigResponseContent:
    """
    Locates the host configuration file in its expected location within the SDK @src/host_configuration/
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "host_configuration", f"{host_id}.json")
    try:
        with open(file_path, "r") as f:
            return GetHostConfigResponseContent.from_dict(json.load(f))
    except Exception as e:
        raise SystemIntegrationError(details=f"Unable to locate host_configuration: {file_path}  Msg: {e}")


def validate_template(template: dict, config: dict, err_str: str):
    """
    Validates the config file contents against the template.
    Template defines the protocol requirements: key: type.
    Basic checks for existence of all the required Keys and values are Not-empty and of the correct type.
    """
    for key in template:
        if key not in config:
            raise SystemIntegrationError(details=f"Invalid {err_str} Missing Key: {key}")
        value = config.get(key)
        if not value:
            raise SystemIntegrationError(details=f"Invalid {err_str} Value Empty for Key: {key}")
        required_type: str = template.get(key)

        # Check the type.
        if required_type == "str":
            if not isinstance(value, str):
                raise SystemIntegrationError(details=f"Invalid {err_str} Key: {key} Expected Type: {required_type}")
        if required_type == "int":
            if not isinstance(value, int):
                raise SystemIntegrationError(details=f"Invalid {err_str} Key: {key} Expected Type: {required_type}")


def upload_file(local_path, presigned_put_remote_path: str, timeout: int, file_type: str):
    """
    Upload a file using the pre-signed URL: presigned_put_remote_path.

    Args:
        local_path: Path to the local file to upload
        presigned_put_remote_path: pre-signed URL (PUT)

    Raises:
        requests.exceptions.RequestException: If the upload fails or times out.
    """
    logger.info(f"Uploading {file_type} file: {local_path[-20:]}... to: {presigned_put_remote_path[-20:]}...")
    with open(local_path, 'rb') as file:
        # Explicitly read the file first to ensure we get a complete copy, not a partially written file.
        with open(local_path, 'rb') as f:
            file_content = f.read()
        try:
            response = requests.put(
                url=presigned_put_remote_path,
                data=file_content,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Could be a temporary network outage.  Keep trying.
            logger.warn(f"File: Could not upload: {e}")
        except Exception as e:
            raise UploadError(f"Unknown error uploading file: {e}") from e
