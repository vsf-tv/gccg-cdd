# SrtListenerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | **str** |  | [optional] 
**port** | **float** |  | 
**minimum_latency_milliseconds** | **float** |  | [default to 3000]
**encryption** | [**DeviceEncryption**](DeviceEncryption.md) |  | [optional] 
**interface** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.srt_listener_transport_protocol import SrtListenerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of SrtListenerTransportProtocol from a JSON string
srt_listener_transport_protocol_instance = SrtListenerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(SrtListenerTransportProtocol.to_json())

# convert the object into a dict
srt_listener_transport_protocol_dict = srt_listener_transport_protocol_instance.to_dict()
# create an instance of SrtListenerTransportProtocol from a dict
srt_listener_transport_protocol_from_dict = SrtListenerTransportProtocol.from_dict(srt_listener_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


