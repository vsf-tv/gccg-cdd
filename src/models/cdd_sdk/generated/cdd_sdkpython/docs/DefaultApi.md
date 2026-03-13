# cdd_sdk_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect**](DefaultApi.md#connect) | **PUT** /connect | 
[**deprovision**](DefaultApi.md#deprovision) | **PUT** /deprovision | 
[**disconnect**](DefaultApi.md#disconnect) | **PUT** /disconnect | 
[**get_configuration**](DefaultApi.md#get_configuration) | **GET** /get_configuration | 
[**get_connection_status**](DefaultApi.md#get_connection_status) | **GET** /get_state | 
[**report_actual_configuration**](DefaultApi.md#report_actual_configuration) | **PUT** /report_actual_configuration | 
[**report_status**](DefaultApi.md#report_status) | **PUT** /report_status | 


# **connect**
> ConnectResponseContent connect(connect_request_content)

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.connect_request_content import ConnectRequestContent
from cdd_sdk_client.models.connect_response_content import ConnectResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)
    connect_request_content = cdd_sdk_client.ConnectRequestContent() # ConnectRequestContent | 

    try:
        api_response = api_instance.connect(connect_request_content)
        print("The response of DefaultApi->connect:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->connect: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connect_request_content** | [**ConnectRequestContent**](ConnectRequestContent.md)|  | 

### Return type

[**ConnectResponseContent**](ConnectResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Connect 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deprovision**
> DeprovisionResponseContent deprovision(host_id, force=force)

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.deprovision_response_content import DeprovisionResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)
    host_id = 'host_id_example' # str | 
    force = True # bool |  (optional)

    try:
        api_response = api_instance.deprovision(host_id, force=force)
        print("The response of DefaultApi->deprovision:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->deprovision: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_id** | **str**|  | 
 **force** | **bool**|  | [optional] 

### Return type

[**DeprovisionResponseContent**](DeprovisionResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Deprovision 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disconnect**
> DisconnectResponseContent disconnect()

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.disconnect_response_content import DisconnectResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)

    try:
        api_response = api_instance.disconnect()
        print("The response of DefaultApi->disconnect:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->disconnect: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**DisconnectResponseContent**](DisconnectResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Disconnect 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_configuration**
> GetConfigurationResponseContent get_configuration()

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.get_configuration_response_content import GetConfigurationResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)

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

# **get_connection_status**
> GetConnectionStatusResponseContent get_connection_status()

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.get_connection_status_response_content import GetConnectionStatusResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_connection_status()
        print("The response of DefaultApi->get_connection_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_connection_status: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetConnectionStatusResponseContent**](GetConnectionStatusResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GetConnectionStatus 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **report_actual_configuration**
> ReportActualConfigurationResponseContent report_actual_configuration(report_actual_configuration_request_content)

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.report_actual_configuration_request_content import ReportActualConfigurationRequestContent
from cdd_sdk_client.models.report_actual_configuration_response_content import ReportActualConfigurationResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)
    report_actual_configuration_request_content = cdd_sdk_client.ReportActualConfigurationRequestContent() # ReportActualConfigurationRequestContent | 

    try:
        api_response = api_instance.report_actual_configuration(report_actual_configuration_request_content)
        print("The response of DefaultApi->report_actual_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->report_actual_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_actual_configuration_request_content** | [**ReportActualConfigurationRequestContent**](ReportActualConfigurationRequestContent.md)|  | 

### Return type

[**ReportActualConfigurationResponseContent**](ReportActualConfigurationResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ReportActualConfiguration 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **report_status**
> ReportStatusResponseContent report_status(report_status_request_content)

### Example


```python
import cdd_sdk_client
from cdd_sdk_client.models.report_status_request_content import ReportStatusRequestContent
from cdd_sdk_client.models.report_status_response_content import ReportStatusResponseContent
from cdd_sdk_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = cdd_sdk_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with cdd_sdk_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cdd_sdk_client.DefaultApi(api_client)
    report_status_request_content = cdd_sdk_client.ReportStatusRequestContent() # ReportStatusRequestContent | 

    try:
        api_response = api_instance.report_status(report_status_request_content)
        print("The response of DefaultApi->report_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->report_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_status_request_content** | [**ReportStatusRequestContent**](ReportStatusRequestContent.md)|  | 

### Return type

[**ReportStatusResponseContent**](ReportStatusResponseContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ReportStatus 200 response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

