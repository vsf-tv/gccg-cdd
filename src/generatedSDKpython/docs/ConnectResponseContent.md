# ConnectResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 
**device_id** | **str** |  | [optional] 
**region** | **str** |  | [optional] 
**pairing_code** | **str** |  | [optional] 
**expires** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.connect_response_content import ConnectResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectResponseContent from a JSON string
connect_response_content_instance = ConnectResponseContent.from_json(json)
# print the JSON string representation of the object
print(ConnectResponseContent.to_json())

# convert the object into a dict
connect_response_content_dict = connect_response_content_instance.to_dict()
# create an instance of ConnectResponseContent from a dict
connect_response_content_from_dict = ConnectResponseContent.from_dict(connect_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


