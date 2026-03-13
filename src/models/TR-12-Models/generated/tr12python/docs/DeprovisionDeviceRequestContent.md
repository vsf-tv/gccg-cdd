# DeprovisionDeviceRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reason** | [**DeprovisionReason**](DeprovisionReason.md) |  | [optional] 
**time** | **float** |  | [optional] 

## Example

```python
from tr12_api_client.models.deprovision_device_request_content import DeprovisionDeviceRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of DeprovisionDeviceRequestContent from a JSON string
deprovision_device_request_content_instance = DeprovisionDeviceRequestContent.from_json(json)
# print the JSON string representation of the object
print(DeprovisionDeviceRequestContent.to_json())

# convert the object into a dict
deprovision_device_request_content_dict = deprovision_device_request_content_instance.to_dict()
# create an instance of DeprovisionDeviceRequestContent from a dict
deprovision_device_request_content_from_dict = DeprovisionDeviceRequestContent.from_dict(deprovision_device_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


