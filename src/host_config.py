import attr
import cattr
from typing import List
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
    device_types: List[str] = attr.ib(
        validator=[
            attr.validators.instance_of(list),
            attr.validators.deep_iterable(
                member_validator=attr.validators.instance_of(str),
                iterable_validator=attr.validators.instance_of(list)
            )
        ]
    )
    thumbnail_max_size_KB: int = attr.field(validator=attr.validators.instance_of(int))
    log_file_max_size_KB: int = attr.field(validator=attr.validators.instance_of(int))
    pairing_url: str = attr.field(validator=attr.validators.instance_of(str))
    auth_url: str = attr.field(validator=attr.validators.instance_of(str))
    online_check_urls: List[str] = attr.ib(
        validator=[
            attr.validators.instance_of(list),
            attr.validators.deep_iterable(
                member_validator=attr.validators.instance_of(str),
                iterable_validator=attr.validators.instance_of(list)
            )
        ]
    )


def get_host_config(host_id: str, device_type: str) -> HostConfig:
    """
    Handles retrieving <host_id>.json, serializing into HostConfig and related exceptions.
    :param host_id:
    :return:
    """
    try:
        config = get_json_from_host_configuration_dir(f"{host_id}.json")
        ret = cattr.structure(config, HostConfig)
    except (TypeError, ValueError, AttributeError) as e:
        raise HostConfigurationError(details=f"Invalid structure.  Msg: {e}") from e
    except Exception as e:
        raise HostConfigurationError(details=f"Can not parse.  Msg: {e}") from e

    if device_type not in ret.device_types:
        raise HostConfigurationError(
            details=f"{host_id} does not support device type {device_type}.  Must be one of {ret.device_types}"
        )
    return ret
