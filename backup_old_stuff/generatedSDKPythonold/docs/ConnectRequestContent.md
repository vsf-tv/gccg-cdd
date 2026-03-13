# ConnectRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registration** | [**DeviceRegistration**](DeviceRegistration.md) |  | 
**host_id** | **str** |  | 

## Example

```python
from openapi_client.models.connect_request_content import ConnectRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectRequestContent from a JSON string
connect_request_content_instance = ConnectRequestContent.from_json(json)
# print the JSON string representation of the object
print(ConnectRequestContent.to_json())

# convert the object into a dict
connect_request_content_dict = connect_request_content_instance.to_dict()
# create an instance of ConnectRequestContent from a dict
connect_request_content_from_dict = ConnectRequestContent.from_dict(connect_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


