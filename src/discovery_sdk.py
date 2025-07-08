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
import base64
import cattr
import time
import json
from jsonschema import validate
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_LOG_ERR, MQTT_LOG_WARNING, MQTT_LOG_DEBUG
from threading import Lock
from typing import Optional
from credentialstore import CredentialStore
from custom_exceptions import (
    ConnectError,
    ClientAPIThrottle,
    InvalidConfigurationError,
    InvalidStatusMessageError,
    MQTTPublishError,
    PairingError,
    ReportStatusError,
    ReportSchemaError,
    SystemIntegrationError,
    CertificatesRotationError,
    InvalidThumbnailSubscription,
    DeprovisionError,
    SSLSetupError,
    InvalidLogsSubscription
)
from custom_logger import logger, CDDLogHandler
from pairing import Pairing
from models import (
    States,
    Configuration,
    ConnectResponse,
    DisconnectResponse,
    ReportStatusResponse,
    GetConfigurationResponse,
    DeprovisionResponse
)
from service_api_models import DeprovisionMessage, CertRotate, Telemetry, LogRequest, ReportMessage
from utils import upload_file

from utils import (
    PublishThrottle,
    publish_message,
    validate_file_exists,
    validate_path_exists_and_writeable,
    OnlineChecker,
    ssl_alpn
)

from host_config import (
    HostConfig,
    get_host_config
)
from thumbnails import ThumbnailManager

SUPPORTED_DEVICE_TYPES = [
    "ENCODER",
    "DECODER",
]  # (see: Message Protocol: SUPPORTED_DEVICE_TYPES)


class CddSdk(object):
    """
    Client Cloud Discovery SDK:
    This class manages connections, disconnections, pairing, authentication, and communication with the cloud service.

    Attributes:
        certs_path (str): read/write path where certs can be found.
                          Will place new certs in <certs_path>/<device_local_id>
        device_local_id (int): Unique ID for the client, ie serial number etc.
        schema_file (str): path to the scoped_schema for this device.

    Raises:
        SystemIntegrationError (see custom_exceptions)
        CertificatesWriteError
    """

    def __init__(
        self,
        certs_path: str,
        device_local_id: str,
        schema_file: str,
        device_type: str,
        log_path: str,
    ):

        self.certs_path: str = certs_path
        self.device_local_id: str = device_local_id
        self.schema_file: str = schema_file
        self.device_type = device_type
        self._log_request = LogRequest()

        # Additional params and classes needed by the SDK.
        self.certs: CredentialStore = CredentialStore(
            self.certs_path, self.device_local_id, host_id="undefined"
        )
        self.logger = CDDLogHandler(
            call_back_function=self._report_logs,
            device_id="unk",
            log_path=log_path
        )
        self._processing_log_put = False  # Failsafe: simply drop sending logs if logs are spewing.
        self._log_spew_detected: int = 0
        self.host_config: Optional[HostConfig] = None
        self.mqtt_client: Optional[mqtt.Client] = None
        self.online_checker: Optional[OnlineChecker] = OnlineChecker([])
        self.thumbnail_manager: ThumbnailManager = ThumbnailManager()
        self.state = States.DISCONNECTED
        self.host_id: str = ""
        self.api_lock = Lock()
        self.throttle = PublishThrottle(
            interval_seconds=1
        )  # Is reset to host-settings when available.

        # Validate we can write certs to the certs_path: Raise Exception.
        validate_path_exists_and_writeable(certs_path)
        # Validate we can load the schema: Raise Exception.
        validate_file_exists(self.schema_file)
        # Validate we can read the schema: Raise Exception.
        try:
            with open(self.schema_file, "r") as f:
                self.schema = json.loads(f.read())
        except Exception as e:
            raise SystemIntegrationError(
                details=f"Failed to load schema file from device: {self.schema}"
            )
        self.telemetry = Telemetry()
        self._reset()

    def shutdown(self):
        """
        Rapidly stops all threads and disconnects from the cloud service in preparation for shutdown
        """
        self.thumbnail_manager.stop_all()
        self.online_checker.stop()
        if self.mqtt_client:
            self.mqtt_client.disconnect()  # inform the service gracefully
            self.mqtt_client.loop_stop()

    def _reset(self):
        """
        Disconnects from the current host if CONNECTED and places in the DISCONNECTED state.
        Resets all settings related to the host and prepares the SDK to make a new connection.
        """
        self.host_id = None  # Unsetting host_id indicates host is no longer/not initialized.
        self.certs = None
        self.configuration = Configuration()
        self._schema_delivered = False
        self._transition(States.DISCONNECTED)
        self.thumbnail_manager.stop_all()
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
        self.mqtt_client = None
        self.telemetry = Telemetry()

    def _initialize_host(self, host_id):
        """
        Prepares the SDK for pairing or connecting to specific host_id.
        """
        self.host_config = get_host_config(host_id, self.device_type)
        self.online_checker = OnlineChecker(self.host_config.online_check_urls)
        self.online_checker.start()
        self.certs = CredentialStore(
            self.certs_path, self.device_local_id, host_id
        )
        self.pairing = Pairing(
            self.certs,
            self.device_type,
            self.host_config.service_id,
            self.host_config.pairing_url,
            self.host_config.auth_url,
        )
        self.host_id = host_id  # Host Initialized

    #
    #  PUBLIC METHODS
    #
    def connect(self, host_id) -> ConnectResponse:
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
            try:
                if not self.host_id or self.host_id != host_id:
                    # Specifying a new/changed host. Ensure we disconnect and reconnect to the new one.
                    self._reset()
                    self._initialize_host(host_id)

                if self._is(States.CONNECTING):
                    # A connection is underway, nothing to do but wait for it.
                    logger.info(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Connecting to the service",
                        online_state=self.online_checker.get_online_state()
                    )

                if self._is(States.CONNECTED):
                    logger.info(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Connected",
                        device_id=self.certs.get_device_id(),
                        region=self.certs.get_region(),
                        online_state=self.online_checker.get_online_state()
                    )

                if self._is(States.RECONNECTING):
                    logger.info(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Reconnecting...",
                        device_id=self.certs.get_device_id(),
                        region=self.certs.get_region(),
                        online_state=self.online_checker.get_online_state()
                    )

                if self._is(States.PAIRING):
                    logger.info(self.state)
                    if self._load_certs():
                        return (
                            self._start_connect()
                        )  # start_connect() will update state as will any callbacks.

                    # Expired?
                    if self.pairing.is_expired():
                        self._reset()
                        return ConnectResponse(
                            success=False,
                            state=self.state,
                            message="Pairing code expired. Reconnect to get a new one.",
                            online_state=self.online_checker.get_online_state()
                        )

                    # OK Poll again for credentials. Will either save.
                    if self.pairing.authenticate_pairing_code():
                        # PAIRING->CONNECTING: Attempt to connect.
                        if (
                            self._load_certs()
                        ):  # Any hard failure will raise an exception.
                            # Reset the throttle to service-settings expectations.
                            self.throttle = PublishThrottle(
                                interval_seconds=self.certs.host_settings.min_interval_pub_seconds
                            )
                            return self._start_connect()

                        # Should never happen. Auth was successful: _load_certs() should pass or raise an exception
                        # Ultimately for this to happen, certs would have to be immediately deleted on obtaining them.
                        self._reset()
                        raise PairingError(
                            "Device was authenticated, but couldn't load certs. Try pairing again."
                        )

                    # Still PAIRING, waiting to be claimed.
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Waiting for device to be claimed",
                        pairing_code=self.pairing.get_pairing_code(),
                        expires=self.pairing.expires_in(),
                        online_state=self.online_checker.get_online_state()
                    )

                if self._is(States.DISCONNECTED):
                    logger.info(self.state)
                    # device has been claimed and authentication succeeded. Connect now.
                    if self._load_certs():
                        # Reset the throttle to service-settings expectations.
                        self.throttle = PublishThrottle(
                            interval_seconds=self.certs.host_settings.min_interval_pub_seconds
                        )
                        return self._start_connect()

                    # Poll for credentials, write them if found
                    # then next time _load_certs() == TRUE.
                    self.pairing.get_new_pairing_code()
                    self._transition(States.PAIRING)
                    logger.info(self.state)
                    # will either get a code or throw exception.

                    return ConnectResponse(
                        success=True,
                        state=States.PAIRING,
                        message="Connecting pending. Waiting for device to be claimed",
                        pairing_code=self.pairing.get_pairing_code(),
                        expires=self.pairing.expires_in(),
                        online_state=self.online_checker.get_online_state()
                    )

            except Exception as e:
                return ConnectResponse(
                    success=False,
                    state=self.state,
                    message=f"Error in connect() {str(e)}",
                    exception=e,
                    online_state=self.online_checker.get_online_state()
                )

    def get_connection_status(self) -> ConnectResponse:
        logger.info("Get Connection Status")
        if self.state in [States.CONNECTED, States.RECONNECTING] and self.certs:
            return ConnectResponse(success=True,
                                   state=self.state,
                                   message="",
                                   region=self.certs.get_region(),
                                   online_state=self.online_checker.get_online_state()
                                   )

        return ConnectResponse(success=True,
                               state=self.state,
                               message="",
                               online_state=self.online_checker.get_online_state()
                               )

    def disconnect(self) -> DisconnectResponse:
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
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Disconnect")
            try:
                # Stops the underlying MQTT Thread. Results in an async _on_disconnect() call.
                logger.info("DISCONNECTING")
                self._reset()
                return DisconnectResponse(
                    success=True, state=States.DISCONNECTED, message="Disconnected"
                )

            except Exception as e:
                logger.info(f"Error in disconnect: {e}")
                return DisconnectResponse(
                    success=False,
                    state=self.state,
                    message=f"Error in disconnect: {e}",
                    exception=e,
                )

    def deprovision(self, force: bool = False) -> DeprovisionResponse:
        """
        Deprovision the device from the host service. Certs/Identify deleted.
        Returns a DisconnectResponse().

        If not CONNECTED, requires force=True.
        SDK will inform the service the user deprovisioned the client if state == CONNECTED.

        Raises:
            None
        """
        # APIs requests should not be called asynchronously.
        with self.api_lock:
            logger.info("Deprovision")
            try:
                if self.state not in [States.CONNECTED, States.CONNECTING] and not force:
                    return DeprovisionResponse(
                        success=False,
                        state=self.state,
                        message="Can only deprovision when CONNECTED or using optional force argument.",
                    )

                if self.state == States.CONNECTED:
                    try:
                        deprovision_message = DeprovisionMessage(
                            reason="Deprovision requested by user",
                            time=int(time.time())
                        )
                        str_payload = json.dumps(cattr.unstructure(deprovision_message))
                    except Exception as e:
                        raise ReportSchemaError(details=str(e)) from e

                    # This should never happen since we are in the CONNECTED state.
                    topics = self.certs.get_topics()
                    if not topics or not self.mqtt_client:
                        raise ConnectError(details="Unable to report schema while not connected")

                    publish_message(
                        client=self.mqtt_client,
                        topic=topics.deprovision_inform_service,
                        payload=str_payload,
                        qos=1,
                        retain=False,
                    )
                    time.sleep(1)  # Let the message be sent, plenty of time.
                else:
                    logger.info("Deprovisioning while DISCONNECTED:  Service will not be informed.")

                self.certs.deprovision()
                self._reset()
                return DeprovisionResponse(
                    success=True,
                    state=States.DISCONNECTED,
                    message="Deprovisioned"
                )

            except Exception as e:
                return DeprovisionResponse(
                    success=False,
                    state=self.state,
                    message=f"Error in Deprovision: {e}",
                    exception=e,
                )

    def get_configuration(self) -> GetConfigurationResponse:
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
                if self.configuration.callback_error:
                    raise InvalidConfigurationError()

                # Configuration is locally cached. If the network is down for a moment, can still get latest
                # if the client so desires.
                logger.info(f"Passing updated configuration_id: {self.configuration.update_id} to client.")
                self.telemetry.passed_config_id = self.configuration.update_id
                return GetConfigurationResponse(
                    success=True,
                    state=self.state,
                    message="Latest configuration provided",
                    configuration=self.configuration,
                )

            except Exception as e:
                self.telemetry.passed_config_id = self.configuration.update_id
                return GetConfigurationResponse(
                    success=False,
                    state=self.state,
                    message=f"Latest valid configuration provided, but a more recent configuration was rejected",
                    configuration=self.configuration,
                    exception=e,
                )

    def report_status(self, instance_schema_compliant_payload: dict) -> ReportStatusResponse:
        """
        Report instance_schema_compliant_payload to the host service:
            status and (current) configuration
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
            try:
                if not self._is(States.CONNECTED):
                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Status update not sent",
                        exception=ReportStatusError(
                            details="Can only Report Status while CONNECTED"
                        ),
                    )

                if not self.throttle.can_publish():
                    logger.info("ReportStatus throttled")
                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Throttled: too many requests",
                        exception=ClientAPIThrottle(details="Request: report_status"),
                    )

                try:
                    validate(schema=self.schema, instance=instance_schema_compliant_payload)
                    self.telemetry.reported_message_valid = True
                except Exception as e:
                    # This result will eventually feed into SDK Telemetry (WIP). Here the
                    # service will be informed about the error condition.
                    try:
                        # Report the failure to the service.
                        logger.exception(f"Invalid status payload: {e}")
                        self.telemetry.reported_message_valid = False
                        status_message: ReportMessage = ReportMessage(cattr.unstructure(self.telemetry), {})
                        self._do_publish_status_message(status_message)
                    except Exception as e:
                        # Returning InvalidStatusMessageError even if publish fails here since the invalid status
                        # message is the high order bit.  Possibly exceptions can be a list?
                        logger.exception(f"Can't publish status. Msg: {e}")

                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Status Send Failed. Schema Validation Failure",
                        exception=InvalidStatusMessageError(details=str(e)),
                    )

                # QOS: 0 is best effort is sufficient for status messages that have a limited
                # value over time and need not be queued, accumulated and resent at a later time.
                try:
                    status_message: ReportMessage = ReportMessage(
                        telemetry=self.telemetry,
                        message=instance_schema_compliant_payload
                    )
                    self._do_publish_status_message(status_message)

                except Exception as e:
                    logger.exception(f"Can't publish status. Msg: {e}")
                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Status update not sent",
                        exception=e,
                    )

                return ReportStatusResponse(
                    success=True, state=self.state, message="Status update sent"
                )

            except Exception as e:
                # This result will eventually feed into SDK Telemetry (WIP). Here the
                # service will be informed about the error condition.
                logger.exception(f"Error in report_status: {e}")
                return ReportStatusResponse(
                    success=False,
                    state=self.state,
                    message=f"Status update not sent: {e}",
                    exception=e,
                )

    #
    # PRIVATE METHODS ---------------------------------------------------
    #
    def _do_publish_status_message(self, status_message: ReportMessage):

        # Publish schema is attempted immediately on on_connect() callback.
        # If that failed, we can try again here and if it fails again we can inform the client.
        if not self._schema_delivered:
            logger.info("Attempting to re-publish schema")
            self._report_schema()

        # This should never happen since the state must be CONNECTED.
        topics = self.certs.get_topics()
        if not topics or not self.mqtt_client:
            raise ReportStatusError(
                details="Skipping publish while not CONNECTED"
            )

        publish_message(
            client=self.mqtt_client,
            topic=topics.report_status,
            payload=json.dumps(cattr.unstructure(status_message)),
            qos=0,
            retain=False,
        )

    # ACK: The callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, reason_code):
        """
        Subscribes to required topics and reports the schema.

        Side effect:
            Records delivery success of the schema to enable re-try and informing the client
            on subsequent report_status() requests.

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
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.

        # This should never happen since we are in the CONNECTED state but callback might have been queued.
        topics = self.certs.get_topics()
        if not topics or not self.mqtt_client:
            raise ConnectError(details="Unable to subscribe while not connected")

        try:
            self.mqtt_client.subscribe(topic=topics.update_configuration)
            self.mqtt_client.message_callback_add(
                sub=topics.update_configuration,
                callback=self._update_configuration_callback,
            )
        except Exception as e:
            raise ConnectError(details=f"Client is unable to subscribe to: {topics.update_configuration}.")

        try:
            self.mqtt_client.subscribe(topic=topics.update_certs)
            self.mqtt_client.message_callback_add(
                sub=topics.update_certs,
                callback=self._update_certs_callback,
            )
        except Exception as e:
            raise ConnectError(details=f"Client is unable to subscribe to: {topics.update_certs}.")

        try:
            self.mqtt_client.subscribe(topic=topics.update_thumbnail)
            self.mqtt_client.message_callback_add(
                sub=topics.update_thumbnail,
                callback=self._update_thumbnail_subscription_callback,
            )
        except Exception as e:
            raise ConnectError(details=f"Client is unable to subscribe to: {topics.update_thumbnail}.")

        try:
            self.mqtt_client.subscribe(topic=topics.deprovision_inform_client)
            self.mqtt_client.message_callback_add(
                sub=topics.deprovision_inform_client,
                callback=self._deprovision_device_callback,
            )
        except Exception as e:
            raise ConnectError(details=f"Client is unable to subscribe to: {topics.deprovision_inform_client}.")

        try:
            self.mqtt_client.subscribe(topic=topics.update_log)
            self.mqtt_client.message_callback_add(
                sub=topics.update_log,
                callback=self._update_log_subscription_callback,
            )
        except Exception as e:
            raise ConnectError(details=f"Client is unable to subscribe to: {topics.update_log}.")

        self._report_schema()  # Service will ignore all but the first schema reported by this device_id.
        self._schema_delivered = True


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

    def _start_connect(self) -> ConnectResponse:
        """
        Attempts a connection once it has been determined a connection can happen: certs are available.

        Results:
            Response() returned directly by connect()

        """
        if self._is([States.RECONNECTING, States.CONNECTED]):
            return ConnectResponse(
                success=True,
                state=self.state,
                message="Already connected or automatically re-connecting",
                device_id=self.certs.get_device_id(),
                region=self.certs.get_region(),
                online_state=self.online_checker.get_online_state()
            )

        if self.mqtt_client and self.state == States.CONNECTING:
            return ConnectResponse(success=True,
                                   state=self.state,
                                   message="Connecting",
                                   online_state=self.online_checker.get_online_state()
                                   )

        try:
            # State will remain CONNECTING until on_connect() callback-> CONNECTED or an exception here -> DISCONNECTED
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
            # Reporting a schema is QOS=1. Will send first and will occupy the in-flight slot
            # until delivered.
            self.mqtt_client.max_inflight_messages_set(1)
            self.mqtt_client.max_queued_messages_set(1)

            self._connect()

            # Mqtt client manages its own execution thread. It will run under the current
            # thread and stay alive to handle pub/sub activities, keep alive, etc.
            self.mqtt_client.loop_start()

            return ConnectResponse(
                success=True,
                state=self.state,
                message="Connection started",
                region=self.certs.get_region(),
                online_state=self.online_checker.get_online_state(),
                device_id=self.certs.get_device_id(),
            )

        except Exception as e:
            logger.exception(f"Error in _start_connect: {e}")
            self._reset()  # transitions to DISCONNECTED

            # This is likely the most common error/exception encountered by the host application
            # as it is entirely possible for the users to initiate connections while the device
            # doesn't have an available network connection, is firewall blocked, etc.
            return ConnectResponse(
                success=False,
                state=self.state,
                message=f"Unable to connect at this time. Check network connection.",
                online_state=self.online_checker.get_online_state(),
                exception=ConnectError(
                    "Unable to make initial connection. Check network connection"
                ),
            )

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
            validate(schema=self.schema, instance=config)
            logger.info("Got a valid update config")
            # Increments the update_id and saves the payload.
            self.configuration.update_configuration(payload=config)
            self.telemetry.received_message_valid = True
            self.telemetry.received_config_id = self.configuration.update_id
        except Exception as e:
            # Validation failure here can only happen if the service failed to validate.
            # Regardless, the SDK will perform its own validation here.

            # This is an asynchronous callback.
            # Persist the error in the Configuration class to inform the next get_configuration() Response.
            self.configuration.update_configuration(callback_error=True)
            self.telemetry.received_message_valid = False
            raise InvalidConfigurationError(details=f"Schema Validation Error: {e}")

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
            certs_rotate: CertRotate = cattr.structure(payload, CertRotate)
            logger.info(f"Got updated credentials rotate message.")
        except Exception as e:
            raise CertificatesRotationError(details="Msg: {e}.")

        try:
            # Replace the device cert and disconnect/reconnect ONLY if changed.
            # Persistent cert message will be handled on a new message or on_connect
            if self.certs.rotate_certs(certs_rotate):
                host_id = self.host_id
                # Caller may see DISCONNECTED/CONNECTING while this processes...may take a few seconds.
                logger.info(f"Momentarily reconnecting using new credentials.")
                self.disconnect()
                time.sleep(1)
                self.connect(host_id)
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
            logger.info(f"Got a new thumbnail subscription request: {tn_json}")
            self.thumbnail_manager.update_thumbnail(tn_json)
        except json.JSONDecodeError as e:
            raise InvalidThumbnailSubscription(details=f"Thumbnail subscription: Could not parse.  Msg: {e}") from e

    def _report_schema(self):
        """
        Report the schema to the host service. Service might only accept this once per session.

        Raises:
            ConnectionError: For all MQTT publish error codes.
            ReportSchemaError
        """
        if not self._is(States.CONNECTED):
            logger.info("Can't report schema when not connected")
            raise ReportSchemaError(details="Can't report schema when not connected")

        # TODO:  Need to check the scoped schema against the protocol schema to ensure it is a
        #   valid subset according to the rules of the protocol. Raise: InvalidSchemaError.

        try:
            str_payload = json.dumps(self.schema)
        except Exception as e:
            raise ReportSchemaError(details=str(e)) from e

        # This should never happen since we are in the CONNECTED state.
        topics = self.certs.get_topics()
        if not topics or not self.mqtt_client:
            raise ConnectError(details="Unable to report schema while not connected")

        # QOS:1 at least once to ensure delivery for CONNECTED state since the schema must be available
        # to the service.
        logger.info("Reporting Schema")
        try:
            publish_message(
                client=self.mqtt_client,
                topic=topics.report_schema,
                payload=str_payload,
                qos=1,
                retain=False,
            )
        except Exception as e:
            raise ReportSchemaError(details=str(e)) from e

        # Informs the class this has been done and need not be re-sent.
        self._schema_delivered = True
        logger.info("Schema delivered")

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
        Callback on service deporvisioning the client.  SDK Will reset the connection.  Subsequent calls to connect()
        will not be successful as the service has invalidated the certs.
        """
        try:
            message_json: dict = json.loads(message.payload.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise DeprovisionError(details=f"Could not parse deprovision payload: {message}.  Msg: {e}") from e
        try:
            deprovision_message: DeprovisionMessage = cattr.structure(message_json, DeprovisionMessage)
            logger.info(f"Service deprovisinoed client at: {deprovision_message.time}. Reason: {deprovision_message.reason}")
            self._reset()
        except Exception as e:
            raise DeprovisionError(details=f"Could not parse deprovision model: {message_json}.  Msg: {e}") from e

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
            self._log_request = cattr.structure(json.loads(message.payload.decode("utf-8")), LogRequest)
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
            if self._log_request.is_valid():
                logger.info(f"Pushing Logs.")
                self.telemetry.logs_reported += 1
                upload_file(log_file_path, self._log_request.remote_path, 5, file_type="log")
            elif self._log_request.expires < int(time.time()):
                logger.info(f"Log subscription expired.")

        except Exception as e:
            logger.exception(f"Can't publish status. Msg: {e}")
        finally:
            self._processing_log_put = False
