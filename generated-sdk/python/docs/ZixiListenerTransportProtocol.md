# ZixiListenerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | **str** |  | 
**ip** | **str** |  | 
**port** | **float** |  | 
**latency_ms** | **float** |  | 

## Example

```python
from openapi_client.models.zixi_listener_transport_protocol import ZixiListenerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of ZixiListenerTransportProtocol from a JSON string
zixi_listener_transport_protocol_instance = ZixiListenerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(ZixiListenerTransportProtocol.to_json())

# convert the object into a dict
zixi_listener_transport_protocol_dict = zixi_listener_transport_protocol_instance.to_dict()
# create an instance of ZixiListenerTransportProtocol from a dict
zixi_listener_transport_protocol_from_dict = ZixiListenerTransportProtocol.from_dict(zixi_listener_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


