import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generatedSDKPython'))

from openapi_client.models.channel_configuration import ChannelConfiguration
from openapi_client.models.router_device_configuration import RouterDeviceConfiguration
from openapi_client.models.channel_state import ChannelState
from openapi_client.models.connection import Connection
from openapi_client.models.transport_protocol import TransportProtocol


def validate_configuration(data_dict: dict):
    try:
        model_instance = RouterDeviceConfiguration.from_dict(obj=data_dict)
        return True, None
    except Exception as e:
        return False, str(e)
