# Channel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**id** | **str** |  | 
**channel_type** | [**ChannelType**](ChannelType.md) |  | [optional] 
**simple_settings** | [**List[Setting]**](Setting.md) |  | [optional] 
**profiles** | [**List[ProfileDefinition]**](ProfileDefinition.md) |  | [optional] 
**connection_protocols** | [**List[SupportedProtocol]**](SupportedProtocol.md) |  | [optional] 

## Example

```python
from openapi_client.models.channel import Channel

# TODO update the JSON string below
json = "{}"
# create an instance of Channel from a JSON string
channel_instance = Channel.from_json(json)
# print the JSON string representation of the object
print(Channel.to_json())

# convert the object into a dict
channel_dict = channel_instance.to_dict()
# create an instance of Channel from a dict
channel_from_dict = Channel.from_dict(channel_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


