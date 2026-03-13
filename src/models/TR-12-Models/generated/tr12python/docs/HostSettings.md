# HostSettings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iot_protocol_name** | **str** |  | 
**pairing_timeout_seconds** | **float** |  | 
**min_interval_pub_seconds** | **float** |  | 
**mqtt_keepalive_seconds** | **float** |  | 
**sub_update_topic** | **str** |  | 
**sub_update_thumbnail_subscription_topic** | **str** |  | 
**pub_report_schema_topic** | **str** |  | 
**pub_report_registration_topic** | **str** |  | 
**pub_report_status_topic** | **str** |  | 
**pub_report_actual_configuration_topic** | **str** |  | 
**sub_update_certs_topic** | **str** |  | 
**pub_deprovision_topic** | **str** |  | 
**sub_deprovision_topic** | **str** |  | 
**sub_update_log_subscription_topic** | **str** |  | 

## Example

```python
from tr12_api_client.models.host_settings import HostSettings

# TODO update the JSON string below
json = "{}"
# create an instance of HostSettings from a JSON string
host_settings_instance = HostSettings.from_json(json)
# print the JSON string representation of the object
print(HostSettings.to_json())

# convert the object into a dict
host_settings_dict = host_settings_instance.to_dict()
# create an instance of HostSettings from a dict
host_settings_from_dict = HostSettings.from_dict(host_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


