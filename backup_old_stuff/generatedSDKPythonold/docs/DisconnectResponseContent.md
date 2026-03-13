# DisconnectResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 

## Example

```python
from openapi_client.models.disconnect_response_content import DisconnectResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of DisconnectResponseContent from a JSON string
disconnect_response_content_instance = DisconnectResponseContent.from_json(json)
# print the JSON string representation of the object
print(DisconnectResponseContent.to_json())

# convert the object into a dict
disconnect_response_content_dict = disconnect_response_content_instance.to_dict()
# create an instance of DisconnectResponseContent from a dict
disconnect_response_content_from_dict = DisconnectResponseContent.from_dict(disconnect_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


