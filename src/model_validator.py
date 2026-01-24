
# Generated model imports
from openapi_client.models.device_registration import DeviceRegistration
from openapi_client.models.device_status import DeviceStatus
from openapi_client.models.device_configuration import DeviceConfiguration

"""
Exceptions will be raised if unable to deserialize into the TR12 models.
"""
def validate_configuration(data_dict: dict) -> DeviceConfiguration:
    # Pydantic handles both camelCase and snake_case via aliases
    return DeviceConfiguration.from_dict(obj=data_dict)

def validate_status(data_dict: dict) -> DeviceStatus:
    # Pydantic handles both camelCase and snake_case via aliases
    return DeviceStatus.from_dict(obj=data_dict)

def validate_registration(data_dict: dict) -> DeviceRegistration:
    # Pydantic handles both camelCase and snake_case via aliases
    reg = DeviceRegistration.from_dict(obj=data_dict)
    return reg

