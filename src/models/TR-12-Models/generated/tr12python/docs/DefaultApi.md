# tr12_api_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**authenticate**](DefaultApi.md#authenticate) | **POST** /authenticate | 
[**deprovision_device**](DefaultApi.md#deprovision_device) | **POST** /internal/deprovision | 
[**get_host_config**](DefaultApi.md#get_host_config) | **GET** /internal/host-config | 
[**get_version**](DefaultApi.md#get_version) | **GET** /internal/version | 
[**pair**](DefaultApi.md#pair) | **POST** /pair | 
[**request_log**](DefaultApi.md#request_log) | **POST** /internal/log | 
[**request_thumbnail**](DefaultApi.md#request_thumbnail) | **POST** /internal/thumbnail | 
[**rotate_certificates**](DefaultApi.md#rotate_certificates) | **POST** /internal/rotate-certs | 


# **authenticate**
> AuthenticateResponseContent authenticate(authenticate_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.authenticate_request_content import AuthenticateRequestContent
from tr12_api_client.models.authenticate_response_content import AuthenticateResponseContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    authenticate_request_content = tr12_api_client.AuthenticateRequestContent() # AuthenticateRequestContent | 

    try:
        api_response = api_instance.authenticate(authenticate_request_content)
        print("The response of DefaultApi->authenticate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->authenticate: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authenticate_request_content** | [**AuthenticateRequestContent**](AuthenticateRequestContent.md)|  | 

### Return type

[**AuthenticateResponseContent**](AuthenticateResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Authenticate 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deprovision_device**
> deprovision_device(deprovision_device_request_content=deprovision_device_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.deprovision_device_request_content import DeprovisionDeviceRequestContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    deprovision_device_request_content = tr12_api_client.DeprovisionDeviceRequestContent() # DeprovisionDeviceRequestContent |  (optional)

    try:
        api_instance.deprovision_device(deprovision_device_request_content=deprovision_device_request_content)
    except Exception as e:
        print("Exception when calling DefaultApi->deprovision_device: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deprovision_device_request_content** | [**DeprovisionDeviceRequestContent**](DeprovisionDeviceRequestContent.md)|  | [optional] 

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
**200** | DeprovisionDevice 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_host_config**
> GetHostConfigResponseContent get_host_config()

### Example


```python
import tr12_api_client
from tr12_api_client.models.get_host_config_response_content import GetHostConfigResponseContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_host_config()
        print("The response of DefaultApi->get_host_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_host_config: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetHostConfigResponseContent**](GetHostConfigResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GetHostConfig 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_version**
> GetVersionResponseContent get_version()

### Example


```python
import tr12_api_client
from tr12_api_client.models.get_version_response_content import GetVersionResponseContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_version()
        print("The response of DefaultApi->get_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_version: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetVersionResponseContent**](GetVersionResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GetVersion 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pair**
> PairResponseContent pair(pair_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.pair_request_content import PairRequestContent
from tr12_api_client.models.pair_response_content import PairResponseContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    pair_request_content = tr12_api_client.PairRequestContent() # PairRequestContent | 

    try:
        api_response = api_instance.pair(pair_request_content)
        print("The response of DefaultApi->pair:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->pair: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pair_request_content** | [**PairRequestContent**](PairRequestContent.md)|  | 

### Return type

[**PairResponseContent**](PairResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Pair 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **request_log**
> request_log(request_log_request_content=request_log_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.request_log_request_content import RequestLogRequestContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    request_log_request_content = tr12_api_client.RequestLogRequestContent() # RequestLogRequestContent |  (optional)

    try:
        api_instance.request_log(request_log_request_content=request_log_request_content)
    except Exception as e:
        print("Exception when calling DefaultApi->request_log: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_log_request_content** | [**RequestLogRequestContent**](RequestLogRequestContent.md)|  | [optional] 

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
**200** | RequestLog 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **request_thumbnail**
> request_thumbnail(request_thumbnail_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.request_thumbnail_request_content import RequestThumbnailRequestContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    request_thumbnail_request_content = tr12_api_client.RequestThumbnailRequestContent() # RequestThumbnailRequestContent | 

    try:
        api_instance.request_thumbnail(request_thumbnail_request_content)
    except Exception as e:
        print("Exception when calling DefaultApi->request_thumbnail: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_thumbnail_request_content** | [**RequestThumbnailRequestContent**](RequestThumbnailRequestContent.md)|  | 

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
**200** | RequestThumbnail 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rotate_certificates**
> rotate_certificates(rotate_certificates_request_content)

### Example


```python
import tr12_api_client
from tr12_api_client.models.rotate_certificates_request_content import RotateCertificatesRequestContent
from tr12_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = tr12_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with tr12_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = tr12_api_client.DefaultApi(api_client)
    rotate_certificates_request_content = tr12_api_client.RotateCertificatesRequestContent() # RotateCertificatesRequestContent | 

    try:
        api_instance.rotate_certificates(rotate_certificates_request_content)
    except Exception as e:
        print("Exception when calling DefaultApi->rotate_certificates: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rotate_certificates_request_content** | [**RotateCertificatesRequestContent**](RotateCertificatesRequestContent.md)|  | 

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
**200** | RotateCertificates 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

