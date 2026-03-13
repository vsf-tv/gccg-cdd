# DeviceEncryption


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aes128** | [**DeviceEncryptionAes128**](DeviceEncryptionAes128.md) |  | 
**aes256** | [**DeviceEncryptionAes256**](DeviceEncryptionAes256.md) |  | 

## Example

```python
from cdd_sdk_client.models.device_encryption import DeviceEncryption

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceEncryption from a JSON string
device_encryption_instance = DeviceEncryption.from_json(json)
# print the JSON string representation of the object
print(DeviceEncryption.to_json())

# convert the object into a dict
device_encryption_dict = device_encryption_instance.to_dict()
# create an instance of DeviceEncryption from a dict
device_encryption_from_dict = DeviceEncryption.from_dict(device_encryption_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


