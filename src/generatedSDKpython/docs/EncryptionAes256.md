# EncryptionAes256


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**passcode** | **str** | A 64-character hexadecimal string. | 

## Example

```python
from openapi_client.models.encryption_aes256 import EncryptionAes256

# TODO update the JSON string below
json = "{}"
# create an instance of EncryptionAes256 from a JSON string
encryption_aes256_instance = EncryptionAes256.from_json(json)
# print the JSON string representation of the object
print(EncryptionAes256.to_json())

# convert the object into a dict
encryption_aes256_dict = encryption_aes256_instance.to_dict()
# create an instance of EncryptionAes256 from a dict
encryption_aes256_from_dict = EncryptionAes256.from_dict(encryption_aes256_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


