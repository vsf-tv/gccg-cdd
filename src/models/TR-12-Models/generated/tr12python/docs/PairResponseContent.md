# PairResponseContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**PairResult**](PairResult.md) |  | 

## Example

```python
from tr12_api_client.models.pair_response_content import PairResponseContent

# TODO update the JSON string below
json = "{}"
# create an instance of PairResponseContent from a JSON string
pair_response_content_instance = PairResponseContent.from_json(json)
# print the JSON string representation of the object
print(PairResponseContent.to_json())

# convert the object into a dict
pair_response_content_dict = pair_response_content_instance.to_dict()
# create an instance of PairResponseContent from a dict
pair_response_content_from_dict = PairResponseContent.from_dict(pair_response_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


