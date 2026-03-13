# ReportActualConfigurationResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**state** | **str** |  | 
**message** | **str** |  | 
**error** | [**ErrorDetails**](ErrorDetails.md) |  | [optional] 

## Example

```python
from cdd_sdk_client.models.report_actual_configuration_response_content import ReportActualConfigurationResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of ReportActualConfigurationResponseContent from a JSON string
report_actual_configuration_response_content_instance = ReportActualConfigurationResponseContent.from_json(json)
# print the JSON string representation of the object
print(ReportActualConfigurationResponseContent.to_json())

# convert the object into a dict
report_actual_configuration_response_content_dict = report_actual_configuration_response_content_instance.to_dict()
# create an instance of ReportActualConfigurationResponseContent from a dict
report_actual_configuration_response_content_from_dict = ReportActualConfigurationResponseContent.from_dict(report_actual_configuration_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


