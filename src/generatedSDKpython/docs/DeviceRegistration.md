# DeviceRegistration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channels** | [**List[Channel]**](Channel.md) |  | 
**simple_settings** | [**List[Setting]**](Setting.md) |  | [optional] 
**thumbnails** | [**List[Thumbnail]**](Thumbnail.md) |  | [optional] 

## Example

```python
from openapi_client.models.device_registration import DeviceRegistration

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceRegistration from a JSON string
device_registration_instance = DeviceRegistration.from_json(json)
# print the JSON string representation of the object
print(DeviceRegistration.to_json())

# convert the object into a dict
device_registration_dict = device_registration_instance.to_dict()
# create an instance of DeviceRegistration from a dict
device_registration_from_dict = DeviceRegistration.from_dict(device_registration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


