#!/usr/bin/env python3

import json
import sys
import os

# Add the build directory to Python path to import generated models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build', 'smithy', 'source', 'python-type-codegen', 'src'))

from cdd_models.models import (
    RouterDeviceConfiguration,
    ChannelConfiguration,
    IdAndValue,
    SettingProfile,
    Connection,
    TransportProtocol,
    SrtCallerTransportProtocol
)

def test_configuration_from_json():
    # Load the JSON configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'payloads', '1_channel_encoder', 'configuration.json')
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    print("Loaded JSON:", json.dumps(config_data, indent=2))
    
    # Use Document to wrap JSON data then deserialize
    from smithy_core.documents import Document, _DocumentDeserializer

    document = Document(config_data)
    deserializer = _DocumentDeserializer(document)
    configuration = RouterDeviceConfiguration.deserialize(deserializer)

    print("Successfully created Configuration object!")
    print(f"Channel ID: {configuration.channels[0].id}")
    print(f"Channel State: {configuration.channels[0].state}")
    print(f"Settings count: {len(configuration.channels[0].settings)}")
    transport_protocol = configuration.channels[0].connection.transport_protocol
    print(f"Transport Protocol: {transport_protocol}")
    if hasattr(transport_protocol, 'value'):
        print(f"SRT Caller IP: {transport_protocol.value.ip}")
    
    return configuration

if __name__ == "__main__":
    try:
        config = test_configuration_from_json()
        print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()