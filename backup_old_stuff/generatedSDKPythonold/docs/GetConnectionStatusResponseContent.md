# GetConnectionStatusResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 

## Example

```python
from openapi_client.models.get_connection_status_response_content import GetConnectionStatusResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of GetConnectionStatusResponseContent from a JSON string
get_connection_status_response_content_instance = GetConnectionStatusResponseContent.from_json(json)
# print the JSON string representation of the object
print(GetConnectionStatusResponseContent.to_json())

# convert the object into a dict
get_connection_status_response_content_dict = get_connection_status_response_content_instance.to_dict()
# create an instance of GetConnectionStatusResponseContent from a dict
get_connection_status_response_content_from_dict = GetConnectionStatusResponseContent.from_dict(get_connection_status_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


