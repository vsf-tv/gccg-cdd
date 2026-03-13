# GetVersionResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | [**ProtocolVersion**](ProtocolVersion.md) |  | 

## Example

```python
from tr12_api_client.models.get_version_response_content import GetVersionResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of GetVersionResponseContent from a JSON string
get_version_response_content_instance = GetVersionResponseContent.from_json(json)
# print the JSON string representation of the object
print(GetVersionResponseContent.to_json())

# convert the object into a dict
get_version_response_content_dict = get_version_response_content_instance.to_dict()
# create an instance of GetVersionResponseContent from a dict
get_version_response_content_from_dict = GetVersionResponseContent.from_dict(get_version_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


