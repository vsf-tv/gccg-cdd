# AuthenticateResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**AuthStatus**](AuthStatus.md) |  | 
**ca_cert** | **str** |  | [optional] 
**device_cert** | **str** |  | [optional] 
**mqtt_uri** | **str** |  | [optional] 
**region** | **str** |  | [optional] 
**host_settings** | [**HostSettings**](HostSettings.md) |  | [optional] 

## Example

```python
from tr12_api_client.models.authenticate_response_content import AuthenticateResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of AuthenticateResponseContent from a JSON string
authenticate_response_content_instance = AuthenticateResponseContent.from_json(json)
# print the JSON string representation of the object
print(AuthenticateResponseContent.to_json())

# convert the object into a dict
authenticate_response_content_dict = authenticate_response_content_instance.to_dict()
# create an instance of AuthenticateResponseContent from a dict
authenticate_response_content_from_dict = AuthenticateResponseContent.from_dict(authenticate_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


