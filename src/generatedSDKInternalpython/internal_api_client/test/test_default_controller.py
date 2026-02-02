import unittest

from flask import json

from internal_api_client.models.authenticate_request_content import AuthenticateRequestContent  # noqa: E501
from internal_api_client.models.authenticate_response_content import AuthenticateResponseContent  # noqa: E501
from internal_api_client.models.deprovision_device_request_content import DeprovisionDeviceRequestContent  # noqa: E501
from internal_api_client.models.get_host_config_response_content import GetHostConfigResponseContent  # noqa: E501
from internal_api_client.models.get_version_response_content import GetVersionResponseContent  # noqa: E501
from internal_api_client.models.pair_request_content import PairRequestContent  # noqa: E501
from internal_api_client.models.pair_response_content import PairResponseContent  # noqa: E501
from internal_api_client.models.request_log_request_content import RequestLogRequestContent  # noqa: E501
from internal_api_client.models.request_thumbnail_request_content import RequestThumbnailRequestContent  # noqa: E501
from internal_api_client.models.rotate_certificates_request_content import RotateCertificatesRequestContent  # noqa: E501
from internal_api_client.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_authenticate(self):
        """Test case for authenticate

        
        """
        authenticate_request_content = {"accessCode":"accessCode","deviceId":"deviceId","pairingCode":"pairingCode"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/authenticate',
            method='POST',
            headers=headers,
            data=json.dumps(authenticate_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_deprovision_device(self):
        """Test case for deprovision_device

        
        """
        deprovision_device_request_content = {"reason":"DEPROVISIONED","time":0.8008281904610115}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/internal/deprovision',
            method='POST',
            headers=headers,
            data=json.dumps(deprovision_device_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_host_config(self):
        """Test case for get_host_config

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/internal/host-config',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_version(self):
        """Test case for get_version

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/internal/version',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_pair(self):
        """Test case for pair

        
        """
        pair_request_content = {"deviceType":"deviceType","csr":"csr","hostId":"hostId","version":"version"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/pair',
            method='POST',
            headers=headers,
            data=json.dumps(pair_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_request_log(self):
        """Test case for request_log

        
        """
        request_log_request_content = {"expires":0.8008281904610115,"remotePath":"remotePath"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/internal/log',
            method='POST',
            headers=headers,
            data=json.dumps(request_log_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_request_thumbnail(self):
        """Test case for request_thumbnail

        
        """
        request_thumbnail_request_content = {"requests":{"key":{"period":0.8008281904610115,"expires":6.027456183070403,"remotePath":"remotePath","localPath":"localPath","maxSizeKilobyte":1.4658129805029452}}}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/internal/thumbnail',
            method='POST',
            headers=headers,
            data=json.dumps(request_thumbnail_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rotate_certificates(self):
        """Test case for rotate_certificates

        
        """
        rotate_certificates_request_content = {"deviceCert":"deviceCert","mqttUri":"mqttUri","region":"region"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/internal/rotate-certs',
            method='POST',
            headers=headers,
            data=json.dumps(rotate_certificates_request_content),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
