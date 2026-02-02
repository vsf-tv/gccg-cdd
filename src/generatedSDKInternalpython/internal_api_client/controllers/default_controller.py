import connexion
from typing import Dict
from typing import Tuple
from typing import Union

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
from internal_api_client import util


def authenticate(body):  # noqa: E501
    """authenticate

     # noqa: E501

    :param authenticate_request_content: 
    :type authenticate_request_content: dict | bytes

    :rtype: Union[AuthenticateResponseContent, Tuple[AuthenticateResponseContent, int], Tuple[AuthenticateResponseContent, int, Dict[str, str]]
    """
    authenticate_request_content = body
    if connexion.request.is_json:
        authenticate_request_content = AuthenticateRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def deprovision_device(body=None):  # noqa: E501
    """deprovision_device

     # noqa: E501

    :param deprovision_device_request_content: 
    :type deprovision_device_request_content: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    deprovision_device_request_content = body
    if connexion.request.is_json:
        deprovision_device_request_content = DeprovisionDeviceRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_host_config():  # noqa: E501
    """get_host_config

     # noqa: E501


    :rtype: Union[GetHostConfigResponseContent, Tuple[GetHostConfigResponseContent, int], Tuple[GetHostConfigResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_version():  # noqa: E501
    """get_version

     # noqa: E501


    :rtype: Union[GetVersionResponseContent, Tuple[GetVersionResponseContent, int], Tuple[GetVersionResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def pair(body):  # noqa: E501
    """pair

     # noqa: E501

    :param pair_request_content: 
    :type pair_request_content: dict | bytes

    :rtype: Union[PairResponseContent, Tuple[PairResponseContent, int], Tuple[PairResponseContent, int, Dict[str, str]]
    """
    pair_request_content = body
    if connexion.request.is_json:
        pair_request_content = PairRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def request_log(body=None):  # noqa: E501
    """request_log

     # noqa: E501

    :param request_log_request_content: 
    :type request_log_request_content: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    request_log_request_content = body
    if connexion.request.is_json:
        request_log_request_content = RequestLogRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def request_thumbnail(body):  # noqa: E501
    """request_thumbnail

     # noqa: E501

    :param request_thumbnail_request_content: 
    :type request_thumbnail_request_content: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    request_thumbnail_request_content = body
    if connexion.request.is_json:
        request_thumbnail_request_content = RequestThumbnailRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def rotate_certificates(body):  # noqa: E501
    """rotate_certificates

     # noqa: E501

    :param rotate_certificates_request_content: 
    :type rotate_certificates_request_content: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    rotate_certificates_request_content = body
    if connexion.request.is_json:
        rotate_certificates_request_content = RotateCertificatesRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
