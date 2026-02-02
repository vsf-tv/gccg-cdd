# RistStreamIdentifier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**synchronization_source** | **float** |  | 
**stream_id** | **str** |  | 

## Example

```python
from openapi_client.models.rist_stream_identifier import RistStreamIdentifier

# TODO update the JSON string below
json = "{}"
# create an instance of RistStreamIdentifier from a JSON string
rist_stream_identifier_instance = RistStreamIdentifier.from_json(json)
# print the JSON string representation of the object
print(RistStreamIdentifier.to_json())

# convert the object into a dict
rist_stream_identifier_dict = rist_stream_identifier_instance.to_dict()
# create an instance of RistStreamIdentifier from a dict
rist_stream_identifier_from_dict = RistStreamIdentifier.from_dict(rist_stream_identifier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


