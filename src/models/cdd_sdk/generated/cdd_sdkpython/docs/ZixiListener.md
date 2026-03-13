# ZixiListener


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**zixi_listener** | [**ZixiListenerTransportProtocol**](ZixiListenerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.zixi_listener import ZixiListener

# TODO update the JSON string below
json = "{}"
# create an instance of ZixiListener from a JSON string
zixi_listener_instance = ZixiListener.from_json(json)
# print the JSON string representation of the object
print(ZixiListener.to_json())

# convert the object into a dict
zixi_listener_dict = zixi_listener_instance.to_dict()
# create an instance of ZixiListener from a dict
zixi_listener_from_dict = ZixiListener.from_dict(zixi_listener_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


