# DeviceEncryptionAes256


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**passcode** | **str** | A 64-character hexadecimal string. | 

## Example

```python
from cdd_sdk_client.models.device_encryption_aes256 import DeviceEncryptionAes256

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceEncryptionAes256 from a JSON string
device_encryption_aes256_instance = DeviceEncryptionAes256.from_json(json)
# print the JSON string representation of the object
print(DeviceEncryptionAes256.to_json())

# convert the object into a dict
device_encryption_aes256_dict = device_encryption_aes256_instance.to_dict()
# create an instance of DeviceEncryptionAes256 from a dict
device_encryption_aes256_from_dict = DeviceEncryptionAes256.from_dict(device_encryption_aes256_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


