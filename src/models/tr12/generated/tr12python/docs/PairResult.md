# PairResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | [**PairSuccessData**](PairSuccessData.md) |  | 
**failure** | [**PairFailureData**](PairFailureData.md) |  | 

## Example

```python
from tr12_api_client.models.pair_result import PairResult

# TODO update the JSON string below
json = "{}"
# create an instance of PairResult from a JSON string
pair_result_instance = PairResult.from_json(json)
# print the JSON string representation of the object
print(PairResult.to_json())

# convert the object into a dict
pair_result_dict = pair_result_instance.to_dict()
# create an instance of PairResult from a dict
pair_result_from_dict = PairResult.from_dict(pair_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


