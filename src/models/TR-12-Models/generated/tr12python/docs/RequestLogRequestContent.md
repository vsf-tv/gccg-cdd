# RequestLogRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expires** | **float** |  | [optional] 
**remote_path** | **str** |  | [optional] 

## Example

```python
from tr12_api_client.models.request_log_request_content import RequestLogRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of RequestLogRequestContent from a JSON string
request_log_request_content_instance = RequestLogRequestContent.from_json(json)
# print the JSON string representation of the object
print(RequestLogRequestContent.to_json())

# convert the object into a dict
request_log_request_content_dict = request_log_request_content_instance.to_dict()
# create an instance of RequestLogRequestContent from a dict
request_log_request_content_from_dict = RequestLogRequestContent.from_dict(request_log_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


