# ZixiCallerTransportProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stream_id** | **str** |  | 
**ip** | **str** |  | 
**port** | **float** |  | 
**minimum_latency_milliseconds** | **float** |  | [default to 3000]
**encryption** | [**DeviceEncryption**](DeviceEncryption.md) |  | [optional] 

## Example

```python
from cdd_sdk_client.models.zixi_caller_transport_protocol import ZixiCallerTransportProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of ZixiCallerTransportProtocol from a JSON string
zixi_caller_transport_protocol_instance = ZixiCallerTransportProtocol.from_json(json)
# print the JSON string representation of the object
print(ZixiCallerTransportProtocol.to_json())

# convert the object into a dict
zixi_caller_transport_protocol_dict = zixi_caller_transport_protocol_instance.to_dict()
# create an instance of ZixiCallerTransportProtocol from a dict
zixi_caller_transport_protocol_from_dict = ZixiCallerTransportProtocol.from_dict(zixi_caller_transport_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


