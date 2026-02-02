# SrtCallerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | **str** |  | [optional] 
**ip** | **str** |  | 
**port** | **float** |  | 
**minimum_latency_milliseconds** | **float** |  | [default to 3000]
**encryption** | [**Encryption**](Encryption.md) |  | [optional] 

## Example

```python
from openapi_client.models.srt_caller_transport_protocol import SrtCallerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of SrtCallerTransportProtocol from a JSON string
srt_caller_transport_protocol_instance = SrtCallerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(SrtCallerTransportProtocol.to_json())

# convert the object into a dict
srt_caller_transport_protocol_dict = srt_caller_transport_protocol_instance.to_dict()
# create an instance of SrtCallerTransportProtocol from a dict
srt_caller_transport_protocol_from_dict = SrtCallerTransportProtocol.from_dict(srt_caller_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


