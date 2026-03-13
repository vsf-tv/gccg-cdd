# PairSuccessData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**pairing_code** | **str** |  | 
**access_code** | **str** |  | 
**pairing_timeout_seconds** | **float** |  | 

## Example

```python
from tr12_api_client.models.pair_success_data import PairSuccessData

# TODO update the JSON string below
json = "{}"
# create an instance of PairSuccessData from a JSON string
pair_success_data_instance = PairSuccessData.from_json(json)
# print the JSON string representation of the object
print(PairSuccessData.to_json())

# convert the object into a dict
pair_success_data_dict = pair_success_data_instance.to_dict()
# create an instance of PairSuccessData from a dict
pair_success_data_from_dict = PairSuccessData.from_dict(pair_success_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


