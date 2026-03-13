import pytest
from unittest.mock import Mock, patch

from pairing import Pairing
from custom_exceptions import (
    PairingError,
    PairingServiceRequestConnectionError,
    PairingServiceRequestTimeoutError,
    PairingServiceResponseError,
)

@pytest.fixture
def mock_certs():
    """Mock CredentialStore for testing"""
    mock = Mock()
    mock.csr = "mock_csr_data"
    return mock


@pytest.fixture
def pairing(mock_certs):
    """Create Pairing instance with mocked dependencies"""
    return Pairing(
        certs=mock_certs,
        device_type="ENCODER",
        host_id="test_host",
        pairing_url="http://test.com/pair",
        auth_url="http://test.com/auth"
    )


class TestPairing:
    
    @patch('pairing.requests.post')
    def test_get_new_pairing_code_success(self, mock_post, pairing):
        """Test successful pairing code generation"""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"pairing_code": "ABC123", "device_id": "dev1", "host_settings": {"pairing_timeout_seconds": 300}}'
        mock_post.return_value.__enter__.return_value = mock_response
        
        result = pairing.get_new_pairing_code()
        
        assert result == True
        assert pairing.pair_response is not None
        mock_post.assert_called_once()
    
    @patch('pairing.requests.post')
    def test_get_new_pairing_code_non_200_status(self, mock_post, pairing):
        """Test non-200 status code handling"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value.__enter__.return_value = mock_response
        
        with pytest.raises(PairingError) as exc_info:
            pairing.get_new_pairing_code()
        
        assert "StatusCode: 400" in str(exc_info.value)
    
    @patch('pairing.requests.post')
    def test_authenticate_pairing_code_success(self, mock_post, pairing):
        """Test successful authentication"""
        # Setup pair_response first
        pairing.pair_response = Mock()
        pairing.pair_response.device_id = "dev1"
        pairing.pair_response.pairing_code = "ABC123"
        pairing.pair_response.access_code = "access123"
        
        # Mock successful auth response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "CLAIMED"}'
        mock_post.return_value.__enter__.return_value = mock_response
        
        result = pairing.authenticate_pairing_code()
        
        assert result == True
        assert pairing.auth_response.status == "CLAIMED"
    
    @patch('pairing.requests.post')
    def test_authenticate_pairing_code_standby(self, mock_post, pairing):
        """Test STANDBY status response"""
        # Setup pair_response first
        pairing.pair_response = Mock()
        pairing.pair_response.device_id = "dev1"
        pairing.pair_response.pairing_code = "ABC123"
        pairing.pair_response.access_code = "access123"
        
        # Mock STANDBY response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "STANDBY"}'
        mock_post.return_value.__enter__.return_value = mock_response
        
        result = pairing.authenticate_pairing_code()
        
        assert result == False
        assert pairing.auth_response.status == "STANDBY"
    
    def test_authenticate_pairing_code_no_pair_response(self, pairing):
        """Test authentication without pair_response"""
        with pytest.raises(PairingError) as exc_info:
            pairing.authenticate_pairing_code()
        
        assert "No pairing code to authenticate" in str(exc_info.value)
    
    @pytest.mark.parametrize("status_code", [400, 401, 500])
    @patch('pairing.requests.post')
    def test_non_200_status_codes(self, mock_post, status_code, pairing):
        """Test various non-200 status codes"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = f'Error {status_code}'
        mock_post.return_value.__enter__.return_value = mock_response
        
        with pytest.raises(PairingError) as exc_info:
            pairing.get_new_pairing_code()
        
        assert f"StatusCode: {status_code}" in str(exc_info.value)