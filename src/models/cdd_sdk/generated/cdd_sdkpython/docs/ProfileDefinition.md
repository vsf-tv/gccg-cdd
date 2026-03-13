# ProfileDefinition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**id** | **str** |  | 
**info** | **str** |  | 

## Example

```python
from cdd_sdk_client.models.profile_definition import ProfileDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileDefinition from a JSON string
profile_definition_instance = ProfileDefinition.from_json(json)
# print the JSON string representation of the object
print(ProfileDefinition.to_json())

# convert the object into a dict
profile_definition_dict = profile_definition_instance.to_dict()
# create an instance of ProfileDefinition from a dict
profile_definition_from_dict = ProfileDefinition.from_dict(profile_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


