# DeviceStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**List[StatusValue]**](StatusValue.md) |  | 
**channels** | [**List[ChannelStatus]**](ChannelStatus.md) |  | [optional] 

## Example

```python
from openapi_client.models.device_status import DeviceStatus

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceStatus from a JSON string
device_status_instance = DeviceStatus.from_json(json)
# print the JSON string representation of the object
print(DeviceStatus.to_json())

# convert the object into a dict
device_status_dict = device_status_instance.to_dict()
# create an instance of DeviceStatus from a dict
device_status_from_dict = DeviceStatus.from_dict(device_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


