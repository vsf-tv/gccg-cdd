# SetConfigurationRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**configuration** | [**RouterDeviceConfiguration**](RouterDeviceConfiguration.md) |  | 

## Example

```python
from openapi_client.models.set_configuration_request_content import SetConfigurationRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of SetConfigurationRequestContent from a JSON string
set_configuration_request_content_instance = SetConfigurationRequestContent.from_json(json)
# print the JSON string representation of the object
print(SetConfigurationRequestContent.to_json())

# convert the object into a dict
set_configuration_request_content_dict = set_configuration_request_content_instance.to_dict()
# create an instance of SetConfigurationRequestContent from a dict
set_configuration_request_content_from_dict = SetConfigurationRequestContent.from_dict(set_configuration_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


