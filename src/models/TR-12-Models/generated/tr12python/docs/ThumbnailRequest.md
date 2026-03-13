# ThumbnailRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **float** |  | [optional] 
**expires** | **float** |  | [optional] 
**max_size_kilobyte** | **float** |  | [optional] 
**local_path** | **str** |  | [optional] 
**remote_path** | **str** |  | [optional] 

## Example

```python
from tr12_api_client.models.thumbnail_request import ThumbnailRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ThumbnailRequest from a JSON string
thumbnail_request_instance = ThumbnailRequest.from_json(json)
# print the JSON string representation of the object
print(ThumbnailRequest.to_json())

# convert the object into a dict
thumbnail_request_dict = thumbnail_request_instance.to_dict()
# create an instance of ThumbnailRequest from a dict
thumbnail_request_from_dict = ThumbnailRequest.from_dict(thumbnail_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


