import attr
import cattr
from custom_exceptions import HostConfigurationError
from utils  import get_json_from_host_configuration_dir


@attr.define
class HostConfig(object):
    """
    Instantiate HostConfig cattr.structure()

    Persist the current host configuration information as specified in the user-supplied host_config.
    Validates the required JSON params as specified in the Discovery Protocol.
    """
    service_id: str = attr.field(validator=attr.validators.instance_of(str))
    service_name: str = attr.field(validator=attr.validators.instance_of(str))
    pairing_url: str = attr.field(validator=attr.validators.instance_of(str))
    auth_url: str = attr.field(validator=attr.validators.instance_of(str))


def get_host_config(host_id) -> HostConfig:
    """
    Handles retrieving <host_id>.json, serializing into HostConfig and related exceptions.
    :param host_id:
    :return:
    """
    try:
        config = get_json_from_host_configuration_dir(f"{host_id}.json")
        return cattr.structure(config, HostConfig)
    except (TypeError, ValueError, AttributeError) as e:
        print(f"HostConfiguration: Payload Invalid.")
        raise HostConfigurationError(details=f"Invalid structure.  Msg: {e}") from e
    except Exception as e:
        print(f"HostConfiguration:  Can not parse.")
        raise HostConfigurationError(details=f"Can not parse.  Msg: {e}") from e
