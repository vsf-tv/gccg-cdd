# GetHostConfigResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service_id** | **str** |  | 
**service_name** | **str** |  | 
**device_types** | **List[str]** |  | 
**thumbnail_max_size_kb** | **float** |  | 
**log_file_max_size_kb** | **float** |  | 
**pairing_url** | **str** |  | 
**auth_url** | **str** |  | 

## Example

```python
from tr12_api_client.models.get_host_config_response_content import GetHostConfigResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of GetHostConfigResponseContent from a JSON string
get_host_config_response_content_instance = GetHostConfigResponseContent.from_json(json)
# print the JSON string representation of the object
print(GetHostConfigResponseContent.to_json())

# convert the object into a dict
get_host_config_response_content_dict = get_host_config_response_content_instance.to_dict()
# create an instance of GetHostConfigResponseContent from a dict
get_host_config_response_content_from_dict = GetHostConfigResponseContent.from_dict(get_host_config_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


