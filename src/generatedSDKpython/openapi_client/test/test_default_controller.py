import unittest

from flask import json

from openapi_client.models.connect_request_content import ConnectRequestContent  # noqa: E501
from openapi_client.models.connect_response_content import ConnectResponseContent  # noqa: E501
from openapi_client.models.deprovision_response_content import DeprovisionResponseContent  # noqa: E501
from openapi_client.models.disconnect_response_content import DisconnectResponseContent  # noqa: E501
from openapi_client.models.get_configuration_response_content import GetConfigurationResponseContent  # noqa: E501
from openapi_client.models.get_connection_status_response_content import GetConnectionStatusResponseContent  # noqa: E501
from openapi_client.models.report_actual_configuration_request_content import ReportActualConfigurationRequestContent  # noqa: E501
from openapi_client.models.report_actual_configuration_response_content import ReportActualConfigurationResponseContent  # noqa: E501
from openapi_client.models.report_status_request_content import ReportStatusRequestContent  # noqa: E501
from openapi_client.models.report_status_response_content import ReportStatusResponseContent  # noqa: E501
from openapi_client.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_connect(self):
        """Test case for connect

        
        """
        connect_request_content = {"hostId":"hostId","registration":{"channels":[{"profileSetting":[{"name":"name","id":"id","info":"info"},{"name":"name","id":"id","info":"info"}],"name":"name","channelType":"SOURCE","id":"id","simpleSettings":[{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"},{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"}],"connectionProtocols":["SRT_LISTENER","SRT_LISTENER"]},{"profileSetting":[{"name":"name","id":"id","info":"info"},{"name":"name","id":"id","info":"info"}],"name":"name","channelType":"SOURCE","id":"id","simpleSettings":[{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"},{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"}],"connectionProtocols":["SRT_LISTENER","SRT_LISTENER"]}],"simpleSettings":[{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"},{"enums":{"defaultValue":"defaultValue","values":["values","values"]},"ranges":{"min":0.8008281904610115,"max":6.027456183070403,"defaultValue":1.4658129805029452},"name":"name","id":"id","info":"info"}],"thumbnails":[{"name":"name","localPath":"localPath","id":"id"},{"name":"name","localPath":"localPath","id":"id"}]}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/connect',
            method='PUT',
            headers=headers,
            data=json.dumps(connect_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_deprovision(self):
        """Test case for deprovision

        
        """
        query_string = [('host_id', 'host_id_example'),
                        ('force', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/deprovision',
            method='PUT',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_disconnect(self):
        """Test case for disconnect

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/disconnect',
            method='PUT',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_configuration(self):
        """Test case for get_configuration

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/get_configuration',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_connection_status(self):
        """Test case for get_connection_status

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/get_state',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_report_actual_configuration(self):
        """Test case for report_actual_configuration

        
        """
        report_actual_configuration_request_content = {"configuration":{"channels":[{"settings":{"simpleSettings":[{"value":"value","key":"key"},{"value":"value","key":"key"}]},"connection":{"transportProtocol":{"srtListener":{"streamId":"streamId","minimumLatencyMilliseconds":6.027456183070403,"encryption":{"aes128":{"passcode":"passcode"}},"port":6190.222739483032,"interface":"interface"}}},"id":"id","state":"ACTIVE"},{"settings":{"simpleSettings":[{"value":"value","key":"key"},{"value":"value","key":"key"}]},"connection":{"transportProtocol":{"srtListener":{"streamId":"streamId","minimumLatencyMilliseconds":6.027456183070403,"encryption":{"aes128":{"passcode":"passcode"}},"port":6190.222739483032,"interface":"interface"}}},"id":"id","state":"ACTIVE"}],"simpleSettings":[{"value":"value","key":"key"},{"value":"value","key":"key"}]}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/report_actual_configuration',
            method='PUT',
            headers=headers,
            data=json.dumps(report_actual_configuration_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_report_status(self):
        """Test case for report_status

        
        """
        report_status_request_content = {"status":{"channels":[{"id":"id","state":"ACTIVE","status":[{"name":"name","value":"value","info":"info"},{"name":"name","value":"value","info":"info"}]},{"id":"id","state":"ACTIVE","status":[{"name":"name","value":"value","info":"info"},{"name":"name","value":"value","info":"info"}]}]}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/report_status',
            method='PUT',
            headers=headers,
            data=json.dumps(report_status_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
