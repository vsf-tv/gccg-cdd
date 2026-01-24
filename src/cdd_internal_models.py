import attr
import datetime
import logging
import json

"""
Internal models for the CDD SDK.  These models are used to define the internal
state of the SDK and are not part of the public API.
"""


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


class JsonFormatter(logging.Formatter):
    """
    Per Host API specification, logs transmitted to the host service must be formatted as follows:
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