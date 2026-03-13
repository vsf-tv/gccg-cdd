# RistListener


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rist_listener** | [**RistListenerTransportProtocol**](RistListenerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.rist_listener import RistListener

# TODO update the JSON string below
json = "{}"
# create an instance of RistListener from a JSON string
rist_listener_instance = RistListener.from_json(json)
# print the JSON string representation of the object
print(RistListener.to_json())

# convert the object into a dict
rist_listener_dict = rist_listener_instance.to_dict()
# create an instance of RistListener from a dict
rist_listener_from_dict = RistListener.from_dict(rist_listener_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


