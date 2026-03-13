# StatusValue


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**info** | **str** |  | 
**value** | **str** |  | 

## Example

```python
from openapi_client.models.status_value import StatusValue

# TODO update the JSON string below
json = "{}"
# create an instance of StatusValue from a JSON string
status_value_instance = StatusValue.from_json(json)
# print the JSON string representation of the object
print(StatusValue.to_json())

# convert the object into a dict
status_value_dict = status_value_instance.to_dict()
# create an instance of StatusValue from a dict
status_value_from_dict = StatusValue.from_dict(status_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


