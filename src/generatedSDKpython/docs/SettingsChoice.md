# SettingsChoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**simple_settings** | [**List[IdAndValue]**](IdAndValue.md) |  | 
**profile** | [**SettingProfile**](SettingProfile.md) |  | 

## Example

```python
from openapi_client.models.settings_choice import SettingsChoice

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsChoice from a JSON string
settings_choice_instance = SettingsChoice.from_json(json)
# print the JSON string representation of the object
print(SettingsChoice.to_json())

# convert the object into a dict
settings_choice_dict = settings_choice_instance.to_dict()
# create an instance of SettingsChoice from a dict
settings_choice_from_dict = SettingsChoice.from_dict(settings_choice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


