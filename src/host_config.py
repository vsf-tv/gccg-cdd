import json
import os
from custom_exceptions import SystemIntegrationError
from utils import (
    get_json_from_host_configuration_dir,
    validate_template
)


class HostConfig(object):
    """
    Instantiate HostConfig via the factory class method: get_valid_host_config().

    Persist the current host configuration information as specified in the user-supplied host_config.
    Validates the required JSON params as specified in the Discovery Protocol.
    """
    service_id: str = ""
    service_name: str = ""
    pairing_url: str = ""
    auth_url: str = ""

    def __init__(self, host_id):
        self.host_id = host_id
        config = get_json_from_host_configuration_dir(f"{host_id}.json")
        self.service_id = config["SERVICE_ID"]
        self.service_name = config["SERVICE_NAME"]
        self.pairing_url = config["PAIRING_URL"]
        self.auth_url = config["AUTH_URL"]

    @classmethod
    def get_valid_host_config(cls, host_id: str):
        host_config_file = f"{host_id}.json"
        host_config: dict = get_json_from_host_configuration_dir(host_config_file)
        host_config_template: dict = get_json_from_host_configuration_dir("host_id.protocol.template.json")
        validate_template(host_config_template, host_config, f"host_config: {host_config_file}")
        return HostConfig(host_id)
