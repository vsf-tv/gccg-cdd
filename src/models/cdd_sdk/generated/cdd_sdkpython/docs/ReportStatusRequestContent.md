# ReportStatusRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**DeviceStatus**](DeviceStatus.md) |  | 

## Example

```python
from cdd_sdk_client.models.report_status_request_content import ReportStatusRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of ReportStatusRequestContent from a JSON string
report_status_request_content_instance = ReportStatusRequestContent.from_json(json)
# print the JSON string representation of the object
print(ReportStatusRequestContent.to_json())

# convert the object into a dict
report_status_request_content_dict = report_status_request_content_instance.to_dict()
# create an instance of ReportStatusRequestContent from a dict
report_status_request_content_from_dict = ReportStatusRequestContent.from_dict(report_status_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


