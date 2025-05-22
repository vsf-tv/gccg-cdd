import attr


@attr.define
class HostSettings:
    """
    This model is defined in the CDD Host Service API.

    Use the class below to serialize/deserialize and validate the host_settings response provided in the Pairing() API.
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
