# GetConfigurationResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 
**configuration** | [**ConfigurationData**](ConfigurationData.md) |  | [optional] 

## Example

```python
from cdd_sdk_client.models.get_configuration_response_content import GetConfigurationResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of GetConfigurationResponseContent from a JSON string
get_configuration_response_content_instance = GetConfigurationResponseContent.from_json(json)
# print the JSON string representation of the object
print(GetConfigurationResponseContent.to_json())

# convert the object into a dict
get_configuration_response_content_dict = get_configuration_response_content_instance.to_dict()
# create an instance of GetConfigurationResponseContent from a dict
get_configuration_response_content_from_dict = GetConfigurationResponseContent.from_dict(get_configuration_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


