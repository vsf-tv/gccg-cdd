import time
import attr


@attr.define
class HostSettings:
    """
    This model is defined in the CDD Host Service API.  See Host Service API
    """
    iot_protocol_name: str = attr.field(validator=attr.validators.instance_of(str))
    pairing_timeout_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    min_interval_pub_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    mqtt_keepalive_seconds: int = attr.field(validator=attr.validators.instance_of(int))
    sub_update_topic: str = attr.field(validator=attr.validators.instance_of(str))
    sub_update_thumbnail_subscription_topic: str = attr.field(validator=attr.validators.instance_of(str))
    pub_report_schema_topic: str = attr.field(validator=attr.validators.instance_of(str))
    pub_report_status_topic: str = attr.field(validator=attr.validators.instance_of(str))
    sub_update_certs_topic: str = attr.field(validator=attr.validators.instance_of(str))
    pub_deprovision_topic: str = attr.field(validator=attr.validators.instance_of(str))
    sub_deprovision_topic: str = attr.field(validator=attr.validators.instance_of(str))


@attr.define
class DeprovisionMessage:
    """
    Deprovision message model from the service.  See Host Service API
    """
    reason: str = attr.field(
        default="none",
        validator=attr.validators.instance_of(str)
    )
    time: int = attr.field(
        default=int(time.time()),
        validator=attr.validators.instance_of(int)
    )


@attr.define
class PairResponse:
    """
    Pair response model from the service. See Host Service API
    """
    device_id: str = attr.field(validator=attr.validators.instance_of(str))
    pairing_code: str = attr.field(validator=attr.validators.instance_of(str))
    access_code: str = attr.field(validator=attr.validators.instance_of(str))
    host_settings: HostSettings = attr.field(validator=attr.validators.instance_of(HostSettings))


@attr.define
class AuthResponse:
    """
    Auth response model from the service. See Host Service API
    """
    status: str = attr.field(validator=attr.validators.instance_of(str))
    ca_cert: str = attr.field(validator=attr.validators.instance_of(str))
    device_cert: str = attr.field(validator=attr.validators.instance_of(str))
    MQTTUri: str = attr.field(validator=attr.validators.instance_of(str))
    region: str = attr.field(validator=attr.validators.instance_of(str))


@attr.define
class ConnectionSettings:
    device_id: str = attr.field(validator=attr.validators.instance_of(str))
    uri: str = attr.field(validator=attr.validators.instance_of(str))
    region: str = attr.field(validator=attr.validators.instance_of(str))