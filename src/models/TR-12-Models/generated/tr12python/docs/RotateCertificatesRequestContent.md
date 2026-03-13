# RotateCertificatesRequestContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mqtt_uri** | **str** |  | 
**device_cert** | **str** |  | 
**region** | **str** |  | 

## Example

```python
from tr12_api_client.models.rotate_certificates_request_content import RotateCertificatesRequestContent

# TODO update the JSON string below
json = "{}"
# create an instance of RotateCertificatesRequestContent from a JSON string
rotate_certificates_request_content_instance = RotateCertificatesRequestContent.from_json(json)
# print the JSON string representation of the object
print(RotateCertificatesRequestContent.to_json())

# convert the object into a dict
rotate_certificates_request_content_dict = rotate_certificates_request_content_instance.to_dict()
# create an instance of RotateCertificatesRequestContent from a dict
rotate_certificates_request_content_from_dict = RotateCertificatesRequestContent.from_dict(rotate_certificates_request_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


