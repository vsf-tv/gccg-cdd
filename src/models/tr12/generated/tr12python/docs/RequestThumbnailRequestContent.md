# RequestThumbnailRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests** | [**Dict[str, ThumbnailRequest]**](ThumbnailRequest.md) |  | 

## Example

```python
from tr12_api_client.models.request_thumbnail_request_content import RequestThumbnailRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of RequestThumbnailRequestContent from a JSON string
request_thumbnail_request_content_instance = RequestThumbnailRequestContent.from_json(json)
# print the JSON string representation of the object
print(RequestThumbnailRequestContent.to_json())

# convert the object into a dict
request_thumbnail_request_content_dict = request_thumbnail_request_content_instance.to_dict()
# create an instance of RequestThumbnailRequestContent from a dict
request_thumbnail_request_content_from_dict = RequestThumbnailRequestContent.from_dict(request_thumbnail_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


