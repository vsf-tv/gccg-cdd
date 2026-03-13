# RistCaller


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rist_caller** | [**RistCallerTransportProtocol**](RistCallerTransportProtocol.md) |  | 

## Example

```python
from cdd_sdk_client.models.rist_caller import RistCaller

# TODO update the JSON string below
json = "{}"
# create an instance of RistCaller from a JSON string
rist_caller_instance = RistCaller.from_json(json)
# print the JSON string representation of the object
print(RistCaller.to_json())

# convert the object into a dict
rist_caller_dict = rist_caller_instance.to_dict()
# create an instance of RistCaller from a dict
rist_caller_from_dict = RistCaller.from_dict(rist_caller_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


