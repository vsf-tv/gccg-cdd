# SrtListener


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**srt_listener** | [**SrtListenerTransportProtocol**](SrtListenerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.srt_listener import SrtListener

# TODO update the JSON string below
json = "{}"
# create an instance of SrtListener from a JSON string
srt_listener_instance = SrtListener.from_json(json)
# print the JSON string representation of the object
print(SrtListener.to_json())

# convert the object into a dict
srt_listener_dict = srt_listener_instance.to_dict()
# create an instance of SrtListener from a dict
srt_listener_from_dict = SrtListener.from_dict(srt_listener_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


