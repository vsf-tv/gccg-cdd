import json
from custom_exceptions import SystemIntegrationError
from utils import (
    get_json_from_host_configuration_dir,
    validate_template
)


class HostSettings(object):
    """
    Must instantiate this class via the factory class method: get_valid_host_settings().

    Host Settings JSON is provided by the host service.
    This Class can be used to validate, write, read to the CredentialSore.
    """
    def __init__(self, host_settings: dict):
        self.iot_protocol_name = host_settings["IOT_PROTOCOL_NAME"]
        self.pairing_timeout_seconds = host_settings["PAIRING_TIMEOUT_SECONDS"]
        self.min_interval_pub_seconds = host_settings["MIN_INTERVAL_PUB_SECONDS"]
        self.mqtt_keepalive_seconds = host_settings["MQTT_KEEPALIVE_SECONDS"]
        self.sub_update_topic = host_settings["SUB_UPDATE_TOPIC"]
        self.pub_report_schema_topic = host_settings["PUB_REPORT_SCHEMA_TOPIC"]
        self.pub_report_status_topic = host_settings["PUB_REPORT_STATUS_TOPIC"]
        self.sub_update_certs_topic = host_settings["SUB_UPDATE_CERTS_TOPIC"]
        self.pub_report_subscription_topic = host_settings["PUB_REPORT_SUBSCRIPTION_TOPIC"]

        print(f"Host Settings: {self.to_dict()}")

    def to_dict(self) -> dict:
        """
        For writing the service-provided host_settings to persistent store.
        """
        return {
            "IOT_PROTOCOL_NAME": self.iot_protocol_name,
            "PAIRING_TIMEOUT_SECONDS": self.pairing_timeout_seconds,
            "MIN_INTERVAL_PUB_SECONDS": self.min_interval_pub_seconds,
            "MQTT_KEEPALIVE_SECONDS": self.mqtt_keepalive_seconds,
            "SUB_UPDATE_TOPIC": self.sub_update_topic,
            "PUB_REPORT_SCHEMA_TOPIC": self.pub_report_schema_topic,
            "PUB_REPORT_STATUS_TOPIC": self.pub_report_status_topic,
            "SUB_UPDATE_CERTS_TOPIC": self.sub_update_certs_topic,
            "PUB_REPORT_SUBSCRIPTION_TOPIC": self.pub_report_subscription_topic
        }

    @classmethod
    def get_valid_host_settings(cls, host_settings: dict):
        """
        Validates the host settings against the expected values.
        """
        host_settings_template: dict = get_json_from_host_configuration_dir("host_settings.protocol.template.json")
        validate_template(host_settings_template, host_settings, f"host-service-response: host_settings")
        return HostSettings(host_settings)


