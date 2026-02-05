# RistListenerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | [**RistStreamIdentifier**](RistStreamIdentifier.md) |  | [optional] 
**port** | **float** |  | 
**minimum_latency_milliseconds** | **float** |  | [default to 3000]
**encryption** | [**DeviceEncryption**](DeviceEncryption.md) |  | [optional] 
**interface** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.rist_listener_transport_protocol import RistListenerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of RistListenerTransportProtocol from a JSON string
rist_listener_transport_protocol_instance = RistListenerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(RistListenerTransportProtocol.to_json())

# convert the object into a dict
rist_listener_transport_protocol_dict = rist_listener_transport_protocol_instance.to_dict()
# create an instance of RistListenerTransportProtocol from a dict
rist_listener_transport_protocol_from_dict = RistListenerTransportProtocol.from_dict(rist_listener_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


