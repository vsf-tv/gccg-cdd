# RouterDeviceConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channels** | [**List[ChannelConfiguration]**](ChannelConfiguration.md) |  | 

## Example

```python
from openapi_client.models.router_device_configuration import RouterDeviceConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of RouterDeviceConfiguration from a JSON string
router_device_configuration_instance = RouterDeviceConfiguration.from_json(json)
# print the JSON string representation of the object
print(RouterDeviceConfiguration.to_json())

# convert the object into a dict
router_device_configuration_dict = router_device_configuration_instance.to_dict()
# create an instance of RouterDeviceConfiguration from a dict
router_device_configuration_from_dict = RouterDeviceConfiguration.from_dict(router_device_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


