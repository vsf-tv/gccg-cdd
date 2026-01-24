# Copyright 2025 Amazon.com Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Standard library imports
import json
import time
from threading import Lock
from typing import Optional

# Third-party imports
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_LOG_DEBUG, MQTT_LOG_ERR, MQTT_LOG_WARNING

# Local application imports - import pairing BEFORE generated models to avoid namespace conflict
from credentialstore import CredentialStore
from custom_exceptions import (
    CertificatesRotationError,
    ClientAPIThrottle,
    ConnectError,
    DeprovisionError,
    InvalidConfigurationError,
    InvalidLogsSubscription,
    InvalidStatusMessageError,
    InvalidThumbnailSubscription,
    MQTTPublishError,
    PairingError,
    ReportRegistrationError,
    ReportStatusError,
    SSLSetupError
)
from custom_logger import CDDLogHandler, logger
from pairing import Pairing
from states import (
    States
)

from model_validator import validate_configuration, validate_registration, validate_status
from thumbnails import ThumbnailManager
from utils import (
    Throttle,
    publish_message,
    ssl_alpn,
    upload_file,
    validate_path_exists_and_writeable,
    get_host_configuration,
    UpdateID
)

# Generated model imports for MQTT payloads
from internal_api_client.models.deprovision_reason import DeprovisionReason
from internal_api_client.models.deprovision_device_request_content import DeprovisionDeviceRequestContent
from internal_api_client.models.request_log_request_content import RequestLogRequestContent
from internal_api_client.models.request_thumbnail_request_content import RequestThumbnailRequestContent
from internal_api_client.models.rotate_certificates_request_content import RotateCertificatesRequestContent
from openapi_client.models.device_registration import DeviceRegistration
from openapi_client.models.device_status import DeviceStatus
from openapi_client.models.device_configuration import DeviceConfiguration

# Generated SDK models
from openapi_client.models.configuration_data import ConfigurationData
from openapi_client.models.connect_response_content import ConnectResponseContent
from openapi_client.models.deprovision_response_content import DeprovisionResponseContent
from openapi_client.models.disconnect_response_content import DisconnectResponseContent
from openapi_client.models.get_configuration_response_content import GetConfigurationResponseContent
from openapi_client.models.get_connection_status_response_content import GetConnectionStatusResponseContent
from openapi_client.models.report_actual_configuration_response_content import ReportActualConfigurationResponseContent
from openapi_client.models.report_status_response_content import ReportStatusResponseContent

from custom_exceptions import exception_to_error_details


class CddSdk(object):
    """
    Client Cloud Discovery SDK:
    This class manages connections, disconnections, pairing, authentication, and communication with the cloud service.

    Attributes:
        certs_path (str): read/write path where certs can be found.
                          Will place new certs in <certs_path>/<device_local_id>
        device_local_id (int): Unique ID for the client, ie serial number etc.
        device_type: SOURCE | DESTINATION | BOTH.
            Service will reject on pairing if the type is not supported
        log_path: a local file path where the SDK will keep rotate logs.
            See: src/custom_logger.py for details.

    Raises:
        SystemIntegrationError (see custom_exceptions)
        CertificatesWriteError
    """

    def __init__(
        self,
        certs_path: str,
        device_local_id: str,
        device_type: str,
        log_path: str,
    ):

        self.certs_path: str = certs_path
        self.device_local_id: str = device_local_id
        self.registration: dict = dict()
        self.device_type = device_type
        self._log_request = RequestLogRequestContent.from_dict({"expires": 0, "remotePath": ""})

        # Additional params and classes needed by the SDK.
        self.certs: CredentialStore = CredentialStore(
            self.certs_path, self.device_local_id, host_id="undefined"
        )
        self.logger = CDDLogHandler(
            call_back_function=self._report_logs,
            device_id="",
            log_path=log_path
        )

        self._processing_log_put = False  # Failsafe: simply drop sending logs if logs are spewing.
        self._log_spew_detected: int = 0
        self.mqtt_client: Optional[mqtt.Client] = None
        self.thumbnail_manager: ThumbnailManager = ThumbnailManager()
        self.state = States.DISCONNECTED
        self.host_id: str = ""
        self.api_lock = Lock()
        self.update_id = UpdateID()
        # Validate we can write certs to the certs_path: Raise Exception.
        validate_path_exists_and_writeable(certs_path)
        self._reset()

    def shutdown(self):
        """
        Rapidly stops all threads and disconnects from the cloud service in preparation for shutdown
        """
        self.thumbnail_manager.stop_all()
        if self.mqtt_client:
            self.mqtt_client.disconnect()  # inform the service gracefully
            self.mqtt_client.loop_stop()

    def _reset(self):
        """
        Disconnects from the current host if CONNECTED and places in the DISCONNECTED state.
        Resets all settings related to the host and prepares the SDK to make a new connection.
        """
        self.registration = {}
        self.update_id = UpdateID()
        self._initialize_throttles(1)
        self.host_id = None  # Unsetting host_id indicates host is no longer/not initialized.
        self.certs = None
        self.logger.update_device_id("")
        self.configuration = ConfigurationData()
        self._registration_delivered = False
        self._transition(States.DISCONNECTED)
        self.thumbnail_manager.stop_all()
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
        self.mqtt_client = None

    def _initialize_throttles(self, interval_seconds: int):
        self.status_throttle = Throttle(
            pub_min_interval=interval_seconds
        )
        self.config_throttle = Throttle(
            pub_min_interval=interval_seconds
        )

    def _initialize_host(self, registration: dict, host_id: str):
        """
        Prepares the SDK for pairing or connecting to specific host_id.
        """
        validate_registration(registration)
        self.registration = registration
        host_config = get_host_configuration(host_id)
        self.certs = CredentialStore(
            self.certs_path, self.device_local_id, host_id
        )
        self.pairing = Pairing(
            self.certs,
            self.device_type,
            host_config.service_id,
            host_config.pairing_url,
            host_config.auth_url,
        )
        self.host_id = host_id  # Host Initialized

    #
    #  PUBLIC METHODS
    #
    def connect(self, registration: dict, host_id: str) -> ConnectResponseContent:
        """
        Entry point for pairing, connect, obtain connection state.

        Returns a ConnectResponse() see: (models: ConnectResponse())
                    success: True | False
                    state: = <see States above> # CONNECTED, DISCONNECTED, PAIRING, ....
                    message: "<A text based informative response>",
                    error: Information about any exceptions handled by the SDK (see models: Error())
                    device_id: <str>      # must be CONNECTED | RECONNECTING>,
                    pairing_code: <str>   # must be PAIRING
                    expires: <int>        # must be PAIRING
        Params:
            host_id: <str> Expects read-able host_config file at: SDK --host_configuration_path/<host_id>.json
        Raises:
            None

        Note:
            This function may construct an exception to inform the Response() but will not raise them unhandled.
        """
        # Only Connect and Disconnect must run synchronously since state conflicts can arise.
        with self.api_lock:
            logger.info("Connect")

            def initialize_if_needed():
                if not self.host_id or self.host_id != host_id:
                    # Specifying a new/changed host. Ensure we disconnect and reconnect to the new one.
                    self._reset()
                    self._initialize_host(registration, host_id)

            def handle_connecting_state():
                # A connection is underway, nothing to do but wait for it.
                return ConnectResponseContent.from_dict({
                    "success": True,
                    "state": self.state.value,
                    "message": "Connecting to the service"
                })

            def handle_connected_state():
                return ConnectResponseContent.from_dict({
                    "success": True,
                    "state": self.state.value,
                    "message": "Connected",
                    "deviceId": self.certs.get_device_id(),
                    "region": self.certs.get_region(),
                })

            def handle_reconnecting_state():
                return ConnectResponseContent.from_dict({
                    "success": True,
                    "state": self.state.value,
                    "message": "Reconnecting...",
                    "deviceId": self.certs.get_device_id(),
                    "region": self.certs.get_region(),
                })

            def handle_pairing_state():
                if self._load_certs():
                    return (
                        self._start_connect()
                    )  # start_connect() will update state as will any callbacks.


                # Expired?
                if self.pairing.is_expired():
                    self._reset()
                    return ConnectResponseContent.from_dict({
                        "success": False,
                        "state": self.state.value,
                        "message": "Pairing code expired. Reconnect to get a new one.",
                    })

                # OK Poll again for credentials. Will either save.
                if self.pairing.authenticate_pairing_code():
                    # PAIRING->CONNECTING: Attempt to connect.
                    if (
                            self._load_certs()
                    ):  # Any hard failure will raise an exception.
                        # Reset the throttle to service-settings expectations.
                        self._initialize_throttles(self.certs.host_settings.min_interval_pub_seconds)
                        return self._start_connect()

                    # Should never happen. Auth was successful: _load_certs() should pass or raise an exception
                    # Ultimately for this to happen, certs would have to be immediately deleted on obtaining them.
                    self._reset()
                    raise PairingError(
                        "Device was authenticated, but couldn't load certs. Try pairing again."
                    )

                # Still PAIRING, waiting to be claimed.
                return ConnectResponseContent.from_dict({
                    "success": True,
                    "state": self.state.value,
                    "message": "Waiting for device to be claimed",
                    "pairingCode": self.pairing.get_pairing_code(),
                    "expires": self.pairing.expires_in(),
                })

            def handle_disconnected_state():
                # device has been claimed and authentication succeeded. Connect now.
                if self._load_certs():
                    # Reset the throttle to service-settings expectations.
                    self.throttle = Throttle(
                        pub_min_interval=self.certs.host_settings.min_interval_pub_seconds
                    )
                    return self._start_connect()

                # Poll for credentials, write them if found
                # then next time _load_certs() == TRUE.
                self.pairing.get_new_pairing_code()
                self._transition(States.PAIRING)
                logger.info(self.state)
                # will either get a code or throw exception.

                return ConnectResponseContent.from_dict({
                    "success": True,
                    "state": States.PAIRING.value,
                    "message": "Connecting pending. Waiting for device to be claimed",
                    "pairingCode": self.pairing.get_pairing_code(),
                    "expires": self.pairing.expires_in(),
                })

            # State-based dispatch - only one handler called
            state_handlers = {
                States.CONNECTING: handle_connecting_state,
                States.CONNECTED: handle_connected_state,
                States.RECONNECTING: handle_reconnecting_state,
                States.PAIRING: handle_pairing_state,
                States.DISCONNECTED: handle_disconnected_state
            }

            try:
                initialize_if_needed()
                handler = state_handlers.get(self.state)
                if handler:
                    logger.info(self.state)
                    return handler()

            except Exception as e:
                # Force a DISCONNECT for all errors connecting related.
                # For example, a transient service host service issue providing a bad
                # pairing response we can't parse.  Need to start with a clean state for
                # any subsequent connection attempt.
                try:
                    logger.info(f"Exception: {str(e)}")
                    self._reset()
                except Exception as e:
                    logger.info(f"Error in DISCONNECTING {str(e)}")

                return ConnectResponseContent.from_dict({
                    "success": False,
                    "state": self.state.value,
                    "message": f"Error in connect() {str(e)}",
                    "error": exception_to_error_details(e),
                })

    def get_connection_status(self) -> GetConnectionStatusResponseContent:
        logger.info("Get Connection Status")

        # Only message and region are impacted by state
        region = None
        if self.state in [States.CONNECTED, States.RECONNECTING] and self.certs:
            region = self.certs.get_region()

        return GetConnectionStatusResponseContent.from_dict({
            "success": True,
            "state": self.state.value,
            "message": "",
        })


    def disconnect(self) -> DisconnectResponseContent:
        """
        Stop the client and disconnect from the host service. Certs/Identify maintained.
        Returns a DisconnectResponse()
             success: True | False
             state: = <see States above> # CONNECTED, DISCONNECTED, PAIRING, ....
             message: "<A text based informative response>",

        Raises:
            None

        Note:
            This function may construct an exception to inform the Response() but will not raise them unhandled.
        """
        with self.api_lock:
            logger.info("Disconnect")

            def perform_disconnect():
                logger.info("DISCONNECTING")
                self._reset()

            # Execute chain
            success, message, exception = True, "Disconnected", None

            try:
                perform_disconnect()
            except Exception as e:
                logger.info(f"Error in disconnect: {e}")
                success, message, exception = False, f"Error in disconnect: {e}", e

            return DisconnectResponseContent.from_dict({
                "success": success,
                "state": States.DISCONNECTED.value,
                "message": message,
                "error": exception_to_error_details(exception)
            })


    def deprovision(self, host_id: str, force: bool = False) -> DeprovisionResponseContent:
        """
        Deprovision the device from the host service. Certs/Identify deleted.
        Returns a DisconnectResponse().

        Requires -f if not CONNECTED to service: <host_id>

        Client should first attempt to connect to <host_id> and then deprovision to inform the service to
        clean up any service-side resources associated with this client.

        Raises:
            None
        """
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Deprovision")

            # Default success case
            success = True
            message = f"Deprovisioned credentials for host: {host_id}"
            exception = None

            if not self._connected_to(host_id) and not force:
                message = f"Must use --force to deprovision client while not CONNECTED to: {host_id} "
                return DeprovisionResponseContent.from_dict({
                    "success": success,
                    "state": self.state.value,
                    "message": message,
                    "error": exception_to_error_details(exception)
                })
            try:
                self._handle_deprovision(host_id=host_id)

            except Exception as e:
                success = False
                message = f"Error in Deprovision: {e}"
                exception = e

            return DeprovisionResponseContent.from_dict({
                "success": success,
                "state": self.state.value,
                "message": message,
                "error": exception_to_error_details(exception)
            })

    def get_configuration(self) -> GetConfigurationResponseContent:
        """
        Gets the latest configuration from the host service for this device.
        The caller can optionally ignore the configuration if the state is not CONNECTED.

        Returns a GetConfigurationResponse()
                     success: True | False
                     state: = <see States above>  # CONNECTED, DISCONNECTED, PAIRING, ....
                     message: "<A text based informative response>",
                     configuration: Configuration
        Raises:
            None

        Note:
            This function may construct an exception to inform the Response() but will not raise them unhandled.
        """
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Get Configuration")
            try:
                # Configuration is locally cached. If the network is down for a moment, can still get latest
                # if the client so desires.
                # Pydantic v2 bug with nested model validation.  We have to call GetConfigurationResponseContent
                # with ConfigurationData.to_dict() and let it validate  the result internally.  The workaround is
                # to pass a dict instead of a model instance:
                retval = GetConfigurationResponseContent.from_dict({
                    "success": True,
                    "state": self.state.value,
                    "message": "Latest configuration provided",
                    "configuration": self.configuration.to_dict()
                })
                return retval
            except Exception as e:
                return GetConfigurationResponseContent.from_dict({
                    "success": False,
                    "state": self.state.value,
                    "message": "Configuration from host service could not be processed locally.",
                    "configuration": None,
                    "error": exception_to_error_details(InvalidConfigurationError("{e}"))
                })

    def report_status(self, payload: dict) -> ReportStatusResponseContent:
        """
        Report compliant status payload to the host service:
        Publishing is internally rate limited (See Throttle).
        Service will handle throttling enforcement by disconnecting or revoking the device if this is a problem.

        Returns a ReportStatusResponse()
                     success: True | False
                     state: = <see States above> # CONNECTED, DISCONNECTED, PAIRING, ....
                     message: "<A text based informative response>",

        Raises:
            None

        Note:
            This function may construct an exception to inform the Response() but will not raise them unhandled.
        """
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Report Status")

            def validate_and_publish():
                try:
                    # Validate and get the model
                    status_model = validate_status(payload)

                except Exception as e:
                    # Report failure to service (original behavior)
                    logger.exception(f"Invalid status payload: {e}")
                    raise InvalidStatusMessageError(str(e))

                # Publish the actual message - use model.to_dict() for camelCase
                try:
                    host = self.certs.get_connected_host_settings()
                    camel_payload = status_model.to_dict()
                    self._do_publish_message(json.dumps(camel_payload), host.pub_report_status_topic)
                except Exception as e:
                    logger.exception(f"Can't publish status. Msg: {e}")
                    raise e

            # Execute chain
            success, message, exception = True, "Status update sent", None

            try:
                self._can_publish_now(self.status_throttle)
                validate_and_publish()
            except ClientAPIThrottle as e:
                success, message, exception = False, "Throttled: too many requests", e
            except ReportStatusError as e:
                success, message, exception = False, "Status update not sent", e
            except InvalidStatusMessageError as e:
                success, message, exception = False, "Status Send Failed.  Validation Failure", e
            except Exception as e:
                logger.exception(f"Error in report_status: {e}")
                success, message, exception = False, f"Status update not sent: {e}", e

            return ReportStatusResponseContent.from_dict({
                "success": success, 
                "state": self.state.value,
                "message": message, 
                "error": exception_to_error_details(exception)
            })

    def report_configuration(self, payload: dict) -> ReportActualConfigurationResponseContent:
        """
        Report the actual (current device state) configuration compliant payload to the host service:
        Nominally a device should apply the configuration returned from get_configuration() API request.
        However, circumstances might result in a difference such as 1) A local device-user override. 2) One or more
        fields in the desired configuration could not be applied or a delay in applying.

        Publishing is rate-limited (See Throttle).
        Service will handle throttling enforcement by disconnecting or revoking the device if this is a problem.

        Returns a ReportConfigurationResponse()
                     success: True | False
                     state: = <see States above> # CONNECTED, DISCONNECTED, PAIRING, ....
                     message: "<A text based informative response>",

        Raises:
            None

        Note:
            This function may construct an exception to inform the Response() but will not raise them unhandled.
        """
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Report Configuration")

            def validate_and_publish():
                try:
                    # Validate and get the model
                    config_model = validate_configuration(payload)
                except Exception as e:
                    # Report failure to service (original behavior)
                    logger.exception(f"Invalid configuration payload: {e}")
                    raise InvalidConfigurationError(str(e))

                # Publish the actual message - use model.to_dict() for camelCase
                try:
                    host = self.certs.get_connected_host_settings()
                    camel_payload = config_model.to_dict()
                    self._do_publish_message(json.dumps(camel_payload), host.pub_report_actual_configuration_topic)
                except Exception as e:
                    logger.exception(f"Can't publish configuration. Msg: {e}")
                    raise e

            # Execute chain
            success, message, exception = True, "Configuration update sent", None

            try:
                self._can_publish_now(self.config_throttle)
                validate_and_publish()
            except ClientAPIThrottle as e:
                success, message, exception = False, "Throttled: too many requests", e
            except ReportStatusError as e:
                success, message, exception = False, "Configuration update not sent", e
            except InvalidConfigurationError as e:
                success, message, exception = False, "Configuration Send Failed.  Validation Failure", e
            except Exception as e:
                logger.exception(f"Error in report_configuration: {e}")
                success, message, exception = False, f"Configuration update not sent: {e}", e

            return ReportActualConfigurationResponseContent.from_dict({
                "success": success,
                "state": self.state.value,
                "message": message,
                "error": exception_to_error_details(exception)
            })


    #
    # PRIVATE METHODS ---------------------------------------------------
    #
    def _do_publish_message(self, message: str, topic: str):

        # Publish registration is attempted immediately on on_connect() callback.
        # Can retry here in case that asynchronous attempt failed.
        if not self._registration_delivered:
            logger.info("Attempting to re-publish registration")
            self._registration_delivered = self._report_registration()

        publish_message(
            client=self.mqtt_client,
            topic=topic,
            payload=message,
            qos=0,
            retain=False,
        )

    # ACK: The callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, reason_code):
        """
        Subscribes to required topics and sends the client supplied registration JSON

        Raises:
            ConnectError: Unlikely since CONNECTED state is checked but being asynchronous a race condition is
                           theoretically possible with rapid looping connect()-disconnect() requests as the
                           mqtt client _on_connect and _on_disconnect callbacks try to keep up.
                           Either way, that condition is handled.
        """
        logger.info(f"OnConnect Callback")
        if reason_code in [mqtt.MQTT_ERR_NO_CONN, mqtt.MQTT_ERR_NO_CONN]:
            raise ConnectError(
                details=f"Credentials were refused or revoked. Deregister and re-pair"
            )

        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectError(
                details=f"Connection failed with result code {reason_code}"
            )

        logger.info("ON CONNECT CALLBACK: code " + str(reason_code))
        self._transition(States.CONNECTED)

        def subscribe_to_topic(topic, callback):
            try:
                self.mqtt_client.subscribe(topic=topic)
                self.mqtt_client.message_callback_add(sub=topic, callback=callback)
            except Exception as e:
                raise ConnectError(details=f"Client is unable to subscribe to: {topic}.")

        # Subscribe to all required topics
        try:
            host = self.certs.get_connected_host_settings()
            subscribe_to_topic(host.sub_update_topic, self._update_configuration_callback)
            subscribe_to_topic(host.sub_update_certs_topic, self._update_certs_callback)
            subscribe_to_topic(host.sub_update_thumbnail_subscription_topic, self._update_thumbnail_subscription_callback)
            subscribe_to_topic(host.sub_deprovision_topic, self._deprovision_device_callback)
            subscribe_to_topic(host.sub_update_log_subscription_topic, self._update_log_subscription_callback)

            # Service will ignore all but the first instance reported by this device_id.
            self._report_registration()
            self._registration_delivered = True
        except Exception as e:
            logger.exception(f"Error in _on_connect: {e}")

    def _on_disconnect(self, client, userdata, flags):
        """
        Asynchronously called on a connection-lost event: Transition from CONNECTED-> RECONNECTING.
        As a result of disconnect() request forcing a client to completely disconnect.
        """
        # Can only transition to RECONNECTING from a CONNECTED state.
        if self._is(States.CONNECTED):
            self._transition(States.RECONNECTING)

    @staticmethod
    def _on_message(client, userdata, msg):
        # This should not be called provided all subscribed topics are mapped to callbacks().
        raise MQTTPublishError(
            f"Got unhandled message on: topic: {msg.topic} payload: {str(msg.payload)}"
        )

    @staticmethod
    def _on_log(client, userdata, level, buf):
        if level == MQTT_LOG_ERR:
            logger.error(f"MQTT Log: {level}: {buf}")
        elif level == MQTT_LOG_WARNING:
            logger.warning(f"MQTT Log: {level}: {buf}")
        elif level == MQTT_LOG_DEBUG:
            logger.debug(f"MQTT Log: {level}: {buf}")
        else:
            logger.info(f"MQTT Log: {level}: {buf}")

    def _start_connect(self) -> ConnectResponseContent:
        """
        Attempts a connection once it has been determined a connection can happen: certs are available.

        Results:
            Response() returned directly by connect()

        """
        if self._is([States.RECONNECTING, States.CONNECTED]):
            return ConnectResponseContent.from_dict({
                "success": True,
                "state": self.state.value,
                "message": "Already connected or automatically re-connecting",
                "deviceId": self.certs.get_device_id(),
                "region": self.certs.get_region(),
            })

        if self.mqtt_client and self.state == States.CONNECTING:
            return ConnectResponseContent.from_dict({
                "success": True,
                "state": self.state.value,
                "message": "Connecting",
            })

        try:
            # State will remain CONNECTING until on_connect() callback-> CONNECTED or an exception here -> DISCONNECTED
            # Protocol Requires clean_session = True to guarantee QOS-0,
            # non-persist messages (e.g., Reboot now) are NOT received when the device connects.
            self._transition(States.CONNECTING)
            self.mqtt_client = mqtt.Client(
                client_id=self.certs.get_device_id(),
                clean_session=True,
                userdata=None,
                transport="tcp",
            )

            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_log = self._on_log
            # Using 1 here since we don't want to accumulate a backlog of status messages.
            # Reporting a registration is QOS=1.  The SDK shall send this first and occupy the in-flight slot
            # until delivered.
            self.mqtt_client.max_inflight_messages_set(1)
            self.mqtt_client.max_queued_messages_set(1)

            self._connect()

            # Mqtt client manages its own execution thread. It will run under the current
            # thread and stay alive to handle pub/sub activities, keep alive, etc.
            self.mqtt_client.loop_start()

            return ConnectResponseContent.from_dict({
                "success": True,
                "state": self.state.value,
                "message": "Connection started",
                "region": self.certs.get_region(),
                "deviceId": self.certs.get_device_id(),
            })

        except Exception as e:
            logger.exception(f"Error in _start_connect: {e}")
            self._reset()  # transitions to DISCONNECTED

            # This is likely the most common error/exception encountered by the host application
            # as it is entirely possible for the users to initiate connections while the device
            # doesn't have an available network connection, is firewall blocked, etc.
            return ConnectResponseContent.from_dict({
                "success": False,
                "state": self.state.value,
                "message": "Unable to connect at this time. Check network connection.",
                "error": exception_to_error_details(ConnectError(
                    "Unable to make initial connection. Check network connection"
                )),
            })

    def _connect(self):

        try:
            ssl_context = ssl_alpn(
                ca_cert=self.certs.ca_cert_file,
                device_cert=self.certs.device_cert_file,
                private_key=self.certs.priv_key_file,
                iot_protocol_name=self.certs.host_settings.iot_protocol_name,
            )
        except Exception as e:
            logger.exception(f"Failed to setup SSL. Msg:{e}")
            raise SSLSetupError(f"Msg:{e}")

        self.mqtt_client.tls_set_context(context=ssl_context)
        logger.info(f"Connecting to: {self.certs.get_uri()}")

        # Port 443 enables MQTT over HTTPs and transparency in most network environments.
        result = self.mqtt_client.connect(
                host=self.certs.get_uri(),
                port=443,
                keepalive=self.certs.host_settings.mqtt_keepalive_seconds,
        )
        logger.info(f"!!!!!!!!!!!!!!!!!!!!!  connect result: {result}")

    def _load_certs(self):
        return self.certs.read_from_filesystem()

    def _update_configuration_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the host_settings.sub_update_topic persistent
        topic. An update here means the service just updated the configuration payload (or we just connected).
        The service expects the client to handle an updated configuration right away when the client is connected.

        Args:
             client, userdata: unused metadata supplied by the mqtt client
             message: JSON configuration payload from the service.

        Side Effect:
            Persist configuration for subsequent Response to client get_configuration() requests.
            Persists any error validating the Configuration, and if found are included in the above Response.
        """
        try:
            config = json.loads(message.payload.decode("utf-8"))
        except json.JSONDecodeError as e:
            # Here we can't even read the JSON.
            raise InvalidConfigurationError(details=str(e.msg))

        try:
            # Check the smithy-generated configuration model in ../generated-sdk/python/openapi_client/models
            # Pydantic handles camelCase via aliases, store as-is
            device_configuration: DeviceConfiguration = validate_configuration(config)
            # Increments the update_id and saves the payload.
            # Must use from_dict() - pydantic constructors don't auto-convert nested dicts to models
            self.configuration = ConfigurationData.from_dict({
                "payload": device_configuration.to_dict(),
                "updateId": self.update_id.get()
            })
        except Exception as e:
            raise InvalidConfigurationError(details=f"Validation Error: {e}")

    def _update_certs_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the host_settings.sub_update_certs_topic
        persistent topic. An update here means the service just updated the credentials payload (or the client just
        connected).  If different from the current device_cert, the client must immediately replace the device_cert,
        disconnect and reconnect.

        * Do not call this function from any function with a lock as this calls disconnect() and connect() both
        of which have locks.

        Args:
             client, userdata: unused metadata supplied by the mqtt client.
             message: str device-cert PEM str format.

        Side Effect:
            Will result in a brief DISCONNECTED, CONNECTING state to any API call.

        """
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            # Pydantic model handles camelCase via aliases
            certs_rotate: RotateCertificatesRequestContent = RotateCertificatesRequestContent.from_dict(payload)
            logger.info(f"Got updated credentials rotate message.")
        except Exception as e:
            raise CertificatesRotationError(details="Msg: {e}.")

        try:
            # Replace the device cert and disconnect/reconnect ONLY if changed.
            # Persistent cert message will be handled on a new message or on_connect
            if self.certs.rotate_certs(certs_rotate):
                host_id = self.host_id
                registration = self.registration
                # Caller may see DISCONNECTED/CONNECTING while this processes...may take a few seconds.
                logger.info(f"Momentarily reconnecting using new credentials.")
                self.disconnect()
                time.sleep(1)
                self.connect(registration=registration, host_id=host_id)
            else:
                logger.info(f"Device cert not changed.  No action taken.")

        except Exception as e:
            raise CertificatesRotationError(details=f"Msg: {e}.")

    def _update_thumbnail_subscription_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the
        host_settings.sub_update_thumbnail_subscription_topic persistent topic.
        An update here means the service just updated the thumbnail subscription payload (or the client just connected).
        The service expects the client to handle an updated thumbnail right away when the client is connected.

        Args:
             client, userdata: unused metadata supplied by the mqtt client.
             message: JSON thumbnail payload from the service.

        Side Effect:
            Persist thumbnail for subsequent Response to client get_thumbnail() requests.
            Persists any error validating the Thumbnail, and if found are included in the above Response.
        """
        try:
            tn_json = json.loads(message.payload.decode("utf-8"))
            # Pydantic model handles camelCase via aliases
            thumbnail_subscription = RequestThumbnailRequestContent.from_dict({
                "requests": tn_json
            })
            logger.info(f"Got a new thumbnail subscription request")
            self.thumbnail_manager.update_thumbnail(thumbnail_subscription)
        except json.JSONDecodeError as e:
            raise InvalidThumbnailSubscription(details=f"Thumbnail subscription: Could not parse.  Msg: {e}") from e

    def _report_registration(self):
        """
        Report the registration to the host service. Service might only accept this once per session.

        Raises:
            ConnectionError: For all MQTT publish error codes.
            ReportRegistrationError
        """
        if not self._is(States.CONNECTED):
            raise ReportRegistrationError(details="Can't report registration when not connected")

        try:
            # Validate and convert registration to camelCase for MQTT
            registration_model = validate_registration(self.registration)
            camel_registration = registration_model.to_dict()
            str_payload = json.dumps(camel_registration)
        except Exception as e:
            raise ReportRegistrationError(details=str(e)) from e

        # QOS:1 at least once to ensure delivery for CONNECTED state since the registration must be available
        # to the service.
        logger.info("Reporting Registration")
        try:
            host = self.certs.get_connected_host_settings()
            publish_message(
                client=self.mqtt_client,
                topic=host.pub_report_registration_topic,
                payload=str_payload,
                qos=1,
                retain=False,
            )
        except Exception as e:
            raise ReportRegistrationError(details=str(e)) from e

        # Informs the class this has been done and need not be re-sent.
        logger.info("Registration delivered")
        return True


    def _is(self, state):
        # Differentiating CONNECTED from RECONNECTING is important to the client,
        # for all practical purposes the SDK state machine will treat them the same.
        if isinstance(state, list):
            return self.state in state
        return self.state == state

    def _transition(self, state):
        if state in [States.CONNECTED, States.CONNECTING]:
            self.logger.update_device_id(self.certs.get_device_id())
        if state in [States.DISCONNECTED]:
            self.logger.dump()  # Push logs on initial connect and right after disconnecting.
        logger.info(f"Setting state to {state}")
        self.state = state

    def _deprovision_device_callback(self, client, userdata, message):
        """
        Callback on service deprovisioning the client. The SDK Will reset the connection and delete credentials.
        The final state here is DISCONNECTED
        Subsequent calls to connect() will start PAIRING
        """
        try:
            message_json: dict = json.loads(message.payload.decode("utf-8"))
            # Pydantic model handles camelCase via aliases
            deprovision_message: DeprovisionDeviceRequestContent = DeprovisionDeviceRequestContent.from_dict(message_json)
            logger.info(f"Service deprovisioned client at: {deprovision_message.time}. Reason: {deprovision_message.reason}")
            # Acknowledge the deprovisioning, then reset the connection to force a re-pairing.
            self._handle_deprovision(host_id=self.host_id)

        except Exception as e:
            raise DeprovisionError(details=f"Error processing deprovision: {message}.  Msg: {e}") from e


    def _update_log_subscription_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the
        host_settings.sub_update_log_subscription_topic persistent topic.
        An update here means the service just updated the log subscription payload (or the client just connected).
        The service expects the client to handle an updated log subscription right away when the client is connected.

        Args:
             client, userdata: unused metadata supplied by the mqtt client.
             message: JSON log subscription payload from the service.

        Side Effect:
            Persist log subscription for subsequent Response to client get_log_subscription() requests.
            Persists any error validating the log subscription, and if found are included in the above Response.
        """
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            # Pydantic model handles camelCase via aliases
            self._log_request = RequestLogRequestContent.from_dict(payload)
            # Updated Request?
            logger.info(f"Got new log request.")
            self.logger.dump()  # Immediately send the latest, we either just connected or a new request came.
        except json.JSONDecodeError as e:
            raise InvalidLogsSubscription(details=f"Log subscription: Could not parse.  Msg: {e}") from e

    def _report_logs(self, log_file_path: str):
        if self._processing_log_put:
            # If we're still processing the last logs due to log spewing, don't accumulate more.
            # Uploading a file should never take longer than the rotate interval unless something bad is happening.
            # If this happens, just drop this batch of logs, which is better than unconstrained mem growth or
            # blocking. The most likely scenario is a backed up PUT (endpoint is offline) combined with some kind of
            # unknown failure mode where logs are spewing. The worst case is that the logs not sent.
            self._log_spew_detected = int(time.time())
            return

        self._processing_log_put = True
        try:
            if self._log_spew_detected:
                # This message of course will of course be sent in the next batch of logs messages.
                logger.error(f"Log spew detected.  Last log spew detected at {self._log_spew_detected}.")
                self._log_spew_detected = 0
            if self._log_request.remote_path and self._log_request.expires > int(time.time()):
                logger.info(f"Pushing Logs.")
                upload_file(log_file_path, self._log_request.remote_path, 5, file_type="log")
            elif self._log_request.expires < int(time.time()):
                logger.info(f"Log subscription expired.")

        except Exception as e:
            logger.exception(f"Can't publish status. Msg: {e}")
        finally:
            self._processing_log_put = False


    def _inform_host_service_deprovision(self, host_id: str):
        # Ack for having received a deprovision message.
        if self._connected_to(host_id):
            logger.info(f"Publishing deprovision message to host service. {host_id}")
            try:
                host = self.certs.get_connected_host_settings()
                deprovision_message = DeprovisionDeviceRequestContent.from_dict({
                    "reason": DeprovisionReason.DEPROVISIONED.value,
                    "time": int(time.time())
                })
                # Use model.to_dict() for camelCase
                camel_payload = deprovision_message.to_dict()
                str_payload = json.dumps(camel_payload)
            except Exception as e:
                raise DeprovisionError(details=str(e)) from e

            publish_message(
                client=self.mqtt_client,
                topic=host.pub_deprovision_topic,
                payload=str_payload,
                qos=1,
                retain=False,
            )
            time.sleep(3)  # Let the message be sent, plenty of time.

    def _handle_deprovision(self, host_id: str):
        """
        Implements deprovision whether initiated by the client or host service.
        Final State: DISCONNECTED
        """
        try:
            if not self._connected_to(host_id):
                # When not connected, we simply delete credentials
                logger.info(f"Deprovisioning client while not CONNECTED: Host-Service will not be informed.")
                self._delete_credentials(host_id=host_id)
            else:
                # Attempt to inform the service
                try:
                    self._inform_host_service_deprovision(host_id=host_id)
                except Exception as e:
                    logger.exception(f"Error informing host service of deprovisioning. Msg: {e}")

                try:
                    self._delete_credentials(host_id=host_id)
                except Exception as e:
                    logger.exception(f"Error deleting credentials. Msg: {e}")

        except Exception as e:
            raise DeprovisionError(details=str(e)) from e
        finally:
            self._reset()

    def _delete_credentials(self, host_id: str):
        # when not connected just
        if not self.host_id or self.host_id == host_id:
            logger.info(f"Deleting credentials for {host_id}.")
            CredentialStore(self.certs_path, self.device_local_id, host_id).deprovision()

    def _connected_to(self, host_id: str):
        return self._is(States.CONNECTED) and host_id == self.host_id


    def _can_publish_now(self, throttle: Throttle):
        if not self._is(States.CONNECTED):
            raise ClientAPIThrottle("Must be CONNECTED to publish message to host.")

        if not throttle.can_publish():
            logger.info("Publish was throttled")
            raise ClientAPIThrottle()