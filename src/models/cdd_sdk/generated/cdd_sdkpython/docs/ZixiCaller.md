# ZixiCaller


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**zixi_caller** | [**ZixiCallerTransportProtocol**](ZixiCallerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.zixi_caller import ZixiCaller

# TODO update the JSON string below
json = "{}"
# create an instance of ZixiCaller from a JSON string
zixi_caller_instance = ZixiCaller.from_json(json)
# print the JSON string representation of the object
print(ZixiCaller.to_json())

# convert the object into a dict
zixi_caller_dict = zixi_caller_instance.to_dict()
# create an instance of ZixiCaller from a dict
zixi_caller_from_dict = ZixiCaller.from_dict(zixi_caller_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


