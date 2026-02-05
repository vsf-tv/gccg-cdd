# RistCallerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | [**RistStreamIdentifier**](RistStreamIdentifier.md) |  | [optional] 
**ip** | **str** |  | 
**port** | **float** |  | 
**minimum_latency_milliseconds** | **float** |  | [default to 3000]
**encryption** | [**DeviceEncryption**](DeviceEncryption.md) |  | [optional] 

## Example

```python
from openapi_client.models.rist_caller_transport_protocol import RistCallerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of RistCallerTransportProtocol from a JSON string
rist_caller_transport_protocol_instance = RistCallerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(RistCallerTransportProtocol.to_json())

# convert the object into a dict
rist_caller_transport_protocol_dict = rist_caller_transport_protocol_instance.to_dict()
# create an instance of RistCallerTransportProtocol from a dict
rist_caller_transport_protocol_from_dict = RistCallerTransportProtocol.from_dict(rist_caller_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


