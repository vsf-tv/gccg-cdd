# ChannelConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**state** | [**ChannelState**](ChannelState.md) |  | 
**settings** | [**SettingsChoice**](SettingsChoice.md) |  | [optional] 
**connection** | [**Connection**](Connection.md) |  | [optional] 

## Example

```python
from openapi_client.models.channel_configuration import ChannelConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of ChannelConfiguration from a JSON string
channel_configuration_instance = ChannelConfiguration.from_json(json)
# print the JSON string representation of the object
print(ChannelConfiguration.to_json())

# convert the object into a dict
channel_configuration_dict = channel_configuration_instance.to_dict()
# create an instance of ChannelConfiguration from a dict
channel_configuration_from_dict = ChannelConfiguration.from_dict(channel_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


