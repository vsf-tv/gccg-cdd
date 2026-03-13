# DeprovisionResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 

## Example

```python
from cdd_sdk_client.models.deprovision_response_content import DeprovisionResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of DeprovisionResponseContent from a JSON string
deprovision_response_content_instance = DeprovisionResponseContent.from_json(json)
# print the JSON string representation of the object
print(DeprovisionResponseContent.to_json())

# convert the object into a dict
deprovision_response_content_dict = deprovision_response_content_instance.to_dict()
# create an instance of DeprovisionResponseContent from a dict
deprovision_response_content_from_dict = DeprovisionResponseContent.from_dict(deprovision_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


