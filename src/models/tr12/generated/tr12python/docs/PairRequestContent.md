# PairRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_type** | **str** |  | 
**host_id** | **str** |  | 
**csr** | **str** |  | 
**version** | **str** |  | 

## Example

```python
from tr12_api_client.models.pair_request_content import PairRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of PairRequestContent from a JSON string
pair_request_content_instance = PairRequestContent.from_json(json)
# print the JSON string representation of the object
print(PairRequestContent.to_json())

# convert the object into a dict
pair_request_content_dict = pair_request_content_instance.to_dict()
# create an instance of PairRequestContent from a dict
pair_request_content_from_dict = PairRequestContent.from_dict(pair_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


