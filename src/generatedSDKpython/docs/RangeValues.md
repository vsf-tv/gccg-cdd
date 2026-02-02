# RangeValues


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min** | **float** |  | 
**max** | **float** |  | 
**default_value** | **float** |  | 

## Example

```python
from openapi_client.models.range_values import RangeValues

# TODO update the JSON string below
json = "{}"
# create an instance of RangeValues from a JSON string
range_values_instance = RangeValues.from_json(json)
# print the JSON string representation of the object
print(RangeValues.to_json())

# convert the object into a dict
range_values_dict = range_values_instance.to_dict()
# create an instance of RangeValues from a dict
range_values_from_dict = RangeValues.from_dict(range_values_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


