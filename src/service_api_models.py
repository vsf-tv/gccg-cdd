import attr
import datetime
import logging
import json
import time
from enum import Enum
from typing import Dict


def not_empty(instance, attribute, value):
    if not value:
        raise ValueError(f"{attribute.name} cannot be empty")


def is_pem(instance, attribute, value):
    req: str = "-----BEGIN CERTIFICATE-----"
    if not value.startswith(req):
        raise ValueError(f"{attribute.name} must start with {req}.  Got: {value}")


def is_csr(instance, attribute, value):
    req: str = "-----BEGIN CERTIFICATE REQUEST-----"
    if not value.startswith(req):
        raise ValueError(f"{attribute.name} must start with {req}.  Got: {value}")


class DeprovisionReason(Enum):
    DEPROVISIONED = "DEPROVISIONED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"

@attr.define
class HostSettings:
    """
    This model is defined in the CDD Host Service API.  See Host Service API
    """
    iot_protocol_name: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pairing_timeout_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    min_interval_pub_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    mqtt_keepalive_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    sub_update_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    sub_update_thumbnail_subscription_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pub_report_schema_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pub_report_registration_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pub_report_status_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    sub_update_certs_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pub_deprovision_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    sub_deprovision_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    sub_update_log_subscription_topic: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )


@attr.define
class PairRequest:
    """
    Host Service API defines the following payload for Pair request
    """
    device_type: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    host_id: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    csr: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty, is_csr)
    )


@attr.define
class PairResponse:
    """
    Host Service API defines the following payload for Pair response
    """
    device_id: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pairing_code: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    access_code: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    host_settings: HostSettings = attr.field(validator=attr.validators.instance_of(HostSettings))



@attr.define
class AuthRequest:
    """
    Host Service API defines the following payload for Authentication request
    """
    device_id: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    pairing_code: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    access_code: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )


@attr.define
class AuthResponse:
    """
    Host Service API defines the following payload for Authentication response
    """
    status: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    ca_cert: str = attr.field(validator=attr.validators.instance_of(str))
    device_cert: str = attr.field(validator=attr.validators.instance_of(str))
    MQTTUri: str = attr.field(validator=attr.validators.instance_of(str))
    region: str = attr.field(validator=attr.validators.instance_of(str))


@attr.define
class ConnectionSettings:
    """
    Client SDK API defines the following payload to persist the client and host service identity.
    """
    device_id: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    uri: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    region: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )


@attr.define
class CertRotate:
    """
    Host Service API defines the following payload for Cert rotation
    """
    MQTTUri: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )
    device_cert: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty, is_pem)
    )
    region: str = attr.field(
        validator=attr.validators.and_(attr.validators.instance_of(str), not_empty)
    )


@attr.define
class DeprovisionMessage:
    """
    Host Service API defines the following payload for a Deprovision Message
    """
    reason: DeprovisionReason = attr.field(
        default=DeprovisionReason.UNKNOWN,
        validator=attr.validators.instance_of(DeprovisionReason)
    )
    time: int = attr.field(
        default=int(time.time()),
        validator=attr.validators.instance_of(int)
    )


@attr.define
class Telemetry:
    """
    Host Service API defines the following payload for a Telemetry Message
    """
    received_config_id: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )
    passed_config_id: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )
    exceptions_raised: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    logs_reported: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    schema_valid: bool = attr.field(
        default=True,
        validator=attr.validators.instance_of(bool)
    )
    reported_message_valid: bool = attr.field(
        default=True,
        validator=attr.validators.instance_of(bool)
    )
    received_message_valid: bool = attr.field(
        default=True,
        validator=attr.validators.instance_of(bool)
    )


@attr.define
class ThumbnailRequest:
    """
    Host Service API defines the following payload for a Thumbnail Request Message

    Params:
        period: Seconds between uploads.

        expires: Epoch time seconds.

        max_size_KB: Host Service may not permit files to exceed this value. Enforcement is up to the Host Service
         and may include throttling, disabling thumbnails and possible de-registration.

        local_path: png or jpg only. Path to the thumbnail image. The SDK expects the application to continually
        update this file at least every 10 seconds (protocol minimum rate). local_path is defined by the application
        in the Instance Schema and provided to the service in the status message. See Message Protocol.

        remote_path: A temporary pre-signed url (PUT).

    """
    period: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    expires: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    max_size_KB: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    local_path: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )
    remote_path: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )

    def is_expired(self) -> bool:
        if self.expires < int(time.time()):
            return True
        return False


@attr.define
class ThumbnailRequests:
    #  A convenience class to persist thumbnail requests for each source
    requests: Dict[str, ThumbnailRequest] = attr.field(factory=dict)


@attr.define
class LogRequest:
    """
    Host Service API defines the following payload for a Log Request Message
    """
    expires: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    remote_path: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )

    def is_valid(self) -> bool:
        if self.expires > int(time.time()) and self.remote_path:
            return True
        return False


@attr.define
class ReportMessage:
    """
    Host Service API defines the following payload for a Report Message
    """
    message: Dict = attr.field(factory=dict)  # Must validate to instance schema


class JsonFormatter(logging.Formatter):
    """
    Per Host API specification, logs transmitted to the host servie must be formatted as follows:
        log_record = {
            'timestamp': 2025-06-11T23:11:03.898068Z  ISO 8601 UTC time.
            'device_id':  <provided by the host service credentials>
            'level': standard logging levels
            'message': <str: log message contents>
            'pathname': <str:  file basename emitting the  message>
            'lineno': <int: line number of file emitting the message>,
            'exception': <optional><str: exception including stack trace>
            'extra_data': <optional><str: extra information>
        }
    """
    def __init__(self,
                 device_id: str = "Notset"):
        super().__init__()
        self._device_id = device_id

    def formatTime(self, record, datefmt=None):
        ct = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
        return ct.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def format(self, record):
        # Create a dictionary with the basic log record attributes
        log_record = {
            'timestamp': self.formatTime(record),
            'device_id':  self._device_id,
            'level': record.levelname,
            'message': record.getMessage(),
            'pathname': record.filename,
            'lineno': record.lineno,
        }
        # Handle exceptions - corrected version
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        # Include exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        # Include any extra attributes that were passed
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)

        return json.dumps(log_record)