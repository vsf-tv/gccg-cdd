# TransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**srt_listener** | [**SrtListenerTransportProtocol**](SrtListenerTransportProtocol.md) |  | 
**srt_caller** | [**SrtCallerTransportProtocol**](SrtCallerTransportProtocol.md) |  | 
**rist_listener** | [**RistListenerTransportProtocol**](RistListenerTransportProtocol.md) |  | 
**rist_caller** | [**RistCallerTransportProtocol**](RistCallerTransportProtocol.md) |  | 
**zixi_listener** | [**ZixiListenerTransportProtocol**](ZixiListenerTransportProtocol.md) |  | 
**zixi_caller** | [**ZixiCallerTransportProtocol**](ZixiCallerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.transport_protocol import TransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of TransportProtocol from a JSON string
transport_protocol_instance = TransportProtocol.from_json(json)
# print the JSON string representation of the object
print(TransportProtocol.to_json())

# convert the object into a dict
transport_protocol_dict = transport_protocol_instance.to_dict()
# create an instance of TransportProtocol from a dict
transport_protocol_from_dict = TransportProtocol.from_dict(transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


