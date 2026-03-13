# PairFailureData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reason** | [**PairFailureReason**](PairFailureReason.md) |  | 

## Example

```python
from tr12_api_client.models.pair_failure_data import PairFailureData

# TODO update the JSON string below
json = "{}"
# create an instance of PairFailureData from a JSON string
pair_failure_data_instance = PairFailureData.from_json(json)
# print the JSON string representation of the object
print(PairFailureData.to_json())

# convert the object into a dict
pair_failure_data_dict = pair_failure_data_instance.to_dict()
# create an instance of PairFailureData from a dict
pair_failure_data_from_dict = PairFailureData.from_dict(pair_failure_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


