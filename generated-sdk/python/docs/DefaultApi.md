# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_configuration**](DefaultApi.md#get_configuration) | **GET** /get_configuration | 
[**set_configuration**](DefaultApi.md#set_configuration) | **PUT** /report_actual_configuration | 


# **get_configuration**
> GetConfigurationResponseContent get_configuration()

### Example


```python
import openapi_client
from openapi_client.models.get_configuration_response_content import GetConfigurationResponseContent
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_configuration()
        print("The response of DefaultApi->get_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_configuration: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetConfigurationResponseContent**](GetConfigurationResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GetConfiguration 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_configuration**
> set_configuration(set_configuration_request_content)

### Example


```python
import openapi_client
from openapi_client.models.set_configuration_request_content import SetConfigurationRequestContent
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    set_configuration_request_content = openapi_client.SetConfigurationRequestContent() # SetConfigurationRequestContent | 

    try:
        api_instance.set_configuration(set_configuration_request_content)
    except Exception as e:
        print("Exception when calling DefaultApi->set_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **set_configuration_request_content** | [**SetConfigurationRequestContent**](SetConfigurationRequestContent.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | SetConfiguration 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

