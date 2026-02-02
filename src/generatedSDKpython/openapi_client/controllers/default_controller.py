import connexion
from typing import Dict
from typing import Tuple
from typing import Union

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
from openapi_client import util


def connect(body):  # noqa: E501
    """connect

     # noqa: E501

    :param connect_request_content: 
    :type connect_request_content: dict | bytes

    :rtype: Union[ConnectResponseContent, Tuple[ConnectResponseContent, int], Tuple[ConnectResponseContent, int, Dict[str, str]]
    """
    connect_request_content = body
    if connexion.request.is_json:
        connect_request_content = ConnectRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def deprovision(host_id, force=None):  # noqa: E501
    """deprovision

     # noqa: E501

    :param host_id: 
    :type host_id: str
    :param force: 
    :type force: bool

    :rtype: Union[DeprovisionResponseContent, Tuple[DeprovisionResponseContent, int], Tuple[DeprovisionResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def disconnect():  # noqa: E501
    """disconnect

     # noqa: E501


    :rtype: Union[DisconnectResponseContent, Tuple[DisconnectResponseContent, int], Tuple[DisconnectResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_configuration():  # noqa: E501
    """get_configuration

     # noqa: E501


    :rtype: Union[GetConfigurationResponseContent, Tuple[GetConfigurationResponseContent, int], Tuple[GetConfigurationResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_connection_status():  # noqa: E501
    """get_connection_status

     # noqa: E501


    :rtype: Union[GetConnectionStatusResponseContent, Tuple[GetConnectionStatusResponseContent, int], Tuple[GetConnectionStatusResponseContent, int, Dict[str, str]]
    """
    return 'do some magic!'


def report_actual_configuration(body):  # noqa: E501
    """report_actual_configuration

     # noqa: E501

    :param report_actual_configuration_request_content: 
    :type report_actual_configuration_request_content: dict | bytes

    :rtype: Union[ReportActualConfigurationResponseContent, Tuple[ReportActualConfigurationResponseContent, int], Tuple[ReportActualConfigurationResponseContent, int, Dict[str, str]]
    """
    report_actual_configuration_request_content = body
    if connexion.request.is_json:
        report_actual_configuration_request_content = ReportActualConfigurationRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def report_status(body):  # noqa: E501
    """report_status

     # noqa: E501

    :param report_status_request_content: 
    :type report_status_request_content: dict | bytes

    :rtype: Union[ReportStatusResponseContent, Tuple[ReportStatusResponseContent, int], Tuple[ReportStatusResponseContent, int, Dict[str, str]]
    """
    report_status_request_content = body
    if connexion.request.is_json:
        report_status_request_content = ReportStatusRequestContent.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
