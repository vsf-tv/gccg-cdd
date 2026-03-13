# ProtocolVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | [optional] [default to '1.0.0']

## Example

```python
from tr12_api_client.models.protocol_version import ProtocolVersion

# TODO update the JSON string below
json = "{}"
# create an instance of ProtocolVersion from a JSON string
protocol_version_instance = ProtocolVersion.from_json(json)
# print the JSON string representation of the object
print(ProtocolVersion.to_json())

# convert the object into a dict
protocol_version_dict = protocol_version_instance.to_dict()
# create an instance of ProtocolVersion from a dict
protocol_version_from_dict = ProtocolVersion.from_dict(protocol_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


