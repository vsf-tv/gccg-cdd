# AuthenticateRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**pairing_code** | **str** |  | 
**access_code** | **str** |  | 

## Example

```python
from tr12_api_client.models.authenticate_request_content import AuthenticateRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of AuthenticateRequestContent from a JSON string
authenticate_request_content_instance = AuthenticateRequestContent.from_json(json)
# print the JSON string representation of the object
print(AuthenticateRequestContent.to_json())

# convert the object into a dict
authenticate_request_content_dict = authenticate_request_content_instance.to_dict()
# create an instance of AuthenticateRequestContent from a dict
authenticate_request_content_from_dict = AuthenticateRequestContent.from_dict(authenticate_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


