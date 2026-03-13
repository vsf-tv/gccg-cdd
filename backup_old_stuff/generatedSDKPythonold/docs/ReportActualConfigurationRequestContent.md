# ReportActualConfigurationRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**configuration** | [**RouterDeviceConfiguration**](RouterDeviceConfiguration.md) |  | 

## Example

```python
from openapi_client.models.report_actual_configuration_request_content import ReportActualConfigurationRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of ReportActualConfigurationRequestContent from a JSON string
report_actual_configuration_request_content_instance = ReportActualConfigurationRequestContent.from_json(json)
# print the JSON string representation of the object
print(ReportActualConfigurationRequestContent.to_json())

# convert the object into a dict
report_actual_configuration_request_content_dict = report_actual_configuration_request_content_instance.to_dict()
# create an instance of ReportActualConfigurationRequestContent from a dict
report_actual_configuration_request_content_from_dict = ReportActualConfigurationRequestContent.from_dict(report_actual_configuration_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


