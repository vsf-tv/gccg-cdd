# .DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getConfiguration**](DefaultApi.md#getConfiguration) | **GET** /get_configuration | 
[**setConfiguration**](DefaultApi.md#setConfiguration) | **PUT** /report_actual_configuration | 


# **getConfiguration**
> GetConfigurationResponseContent getConfiguration()


### Example


```typescript
import { createConfiguration, DefaultApi } from 'ConfigurationServiceSDK';

const configuration = createConfiguration();
const apiInstance = new DefaultApi(configuration);

const request = {};

const data = await apiInstance.getConfiguration(request);
console.log('API called successfully. Returned data:', data);
```


### Parameters
This endpoint does not need any parameter.


### Return type

**GetConfigurationResponseContent**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GetConfiguration 200 response |  -  |

[[Back to top]](#) [[Back to API list]](README.md#documentation-for-api-endpoints) [[Back to Model list]](README.md#documentation-for-models) [[Back to README]](README.md)

# **setConfiguration**
> void setConfiguration(setConfigurationRequestContent)


### Example


```typescript
import { createConfiguration, DefaultApi } from 'ConfigurationServiceSDK';
import type { DefaultApiSetConfigurationRequest } from 'ConfigurationServiceSDK';

const configuration = createConfiguration();
const apiInstance = new DefaultApi(configuration);

const request: DefaultApiSetConfigurationRequest = {
  
  setConfigurationRequestContent: {
    configuration: {
      channels: [
        {
          id: "id_example",
          state: "ACTIVE",
          settings: [
            {
              id: "id_example",
              value: "value_example",
            },
          ],
          settingProfile: {
            id: "id_example",
          },
          connection: {
            transportProtocol: null,
          },
        },
      ],
    },
  },
};

const data = await apiInstance.setConfiguration(request);
console.log('API called successfully. Returned data:', data);
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **setConfigurationRequestContent** | **SetConfigurationRequestContent**|  |


### Return type

**void**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | SetConfiguration 200 response |  -  |

[[Back to top]](#) [[Back to API list]](README.md#documentation-for-api-endpoints) [[Back to Model list]](README.md#documentation-for-models) [[Back to README]](README.md)


