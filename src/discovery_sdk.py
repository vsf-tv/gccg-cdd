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
import time
from threading import Lock
import json
from jsonschema import validate
import paho.mqtt.client as mqtt
from typing import Union
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
    CertificatesError
)

from pairing import Pairing
from models import (
    States,
    Configuration,
    ConnectResponse,
    DisconnectResponse,
    ReportStatusResponse,
    GetConfigurationResponse,
)
from utils import (
    PublishThrottle,
    publish_message,
    validate_file_exists,
    validate_path_exists_and_writeable,
    ssl_alpn,
)

from host_config import HostConfig

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
        self, certs_path: str, device_local_id: str, schema_file: str, device_type: str
    ):
        if device_type not in SUPPORTED_DEVICE_TYPES:
            raise SystemIntegrationError(
                details=f"Device type: {device_type} is not supported. Must be one of: {SUPPORTED_DEVICE_TYPES}"
            )
        self.certs_path: str = certs_path
        self.device_local_id: str = device_local_id
        self.schema_file: str = schema_file
        self.device_type = device_type

        # Additional params and classes needed by the SDK.
        self.certs: Union[CredentialStore, None] = None
        self.host_config: Union[HostConfig, None] = None
        self.mqtt_client: Union[mqtt.Client, None] = None
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
        self._reset()

    def _reset(self):
        """
        Disconnects from the current host if CONNECTED and places in the DISCONNECTED state.
        Resets all settings related to the host and prepares the SDK to make a new connection.
        """
        self.host_id = None
        self.certs = None
        self.configuration = Configuration()
        self._schema_delivered = False
        self._transition(States.DISCONNECTED)
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
        self.mqtt_client = None

    def _initialize_host(self, host_id):
        """
        Prepares the SDK for pairing or connecting to specific host_id.
        """
        self.host_id = host_id
        self.host_config = HostConfig.get_valid_host_config(self.host_id)
        self.certs = CredentialStore(
            self.certs_path, self.device_local_id, self.host_config.host_id
        )
        self.pairing = Pairing(
            self.certs,
            self.device_type,
            self.host_config.pairing_url,
            self.host_config.auth_url,
        )

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
            try:
                if not self.host_id or self.host_id != host_id:
                    # Specifying a new/changed host. Ensure we disconnect and reconnect to the new one.
                    self._reset()
                    self._initialize_host(host_id)

                if self._is(States.CONNECTING):
                    # A connection is underway, nothing to do but wait for it.
                    print(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Connecting to the service",
                    )

                if self._is(States.CONNECTED):
                    print(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Connected",
                        device_id=self.certs.device_id,
                    )

                if self._is(States.RECONNECTING):
                    print(self.state)
                    return ConnectResponse(
                        success=True,
                        state=self.state,
                        message="Reconnecting...",
                        device_id=self.certs.device_id,
                    )

                if self._is(States.PAIRING):
                    print(self.state)
                    if self._load_certs():
                        return (
                            self._start_connect()
                        )  # start_connect() will update state as will any callbacks.

                    # Expired?
                    if self.pairing.is_expired():
                        self._reset()
                        return ConnectResponse(
                            success=False,
                            state=States.DISCONNECTED,
                            message="Pairing code expired. Reconnect to get a new one.",
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
                        raise PairingError(
                            "Device was authenticated, but couldn't load certs. Try pairing again"
                        )

                    # Still PAIRING, waiting to be claimed.
                    return ConnectResponse(
                        success=True,
                        state=States.PAIRING,
                        message="Waiting for device to be claimed",
                        pairing_code=self.pairing.pairing_code,
                        expires=self.pairing.expires_in(),
                    )

                if self._is(States.DISCONNECTED):
                    print(self.state)
                    # device has been claimed and authentication succeeded. Connect now.
                    if self._load_certs():
                        # Reset the throttle to service-settings expectations.
                        self.throttle = PublishThrottle(
                            interval_seconds=self.certs.host_settings.min_interval_pub_seconds
                        )
                        return self._start_connect()

                    # Poll for credentials, write them if found
                    # then next time _load_certs() == TRUE.
                    self._transition(States.PAIRING)
                    print(self.state)

                    # will either get a code or throw exception.
                    self.pairing.get_new_pairing_code()
                    return ConnectResponse(
                        success=True,
                        state=States.PAIRING,
                        message="Connecting pending. Waiting for device to be claimed",
                        pairing_code=self.pairing.pairing_code,
                        expires=self.pairing.expires_in(),
                    )

            except Exception as e:
                return ConnectResponse(
                    success=False,
                    state=self.state,
                    message=f"Error in connect() {e}",
                    exception=e,
                )

    # TODO: Might remove this since connect() returns the same response in addition to
    #       driving the connection process if not yet connected.
    def get_connection_status(self) -> ConnectResponse:
        # Get client status: CONNECTED, Etc.
        return ConnectResponse(success=True, state=self.state, message="")

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
            try:
                # Stops the underlying MQTT Thread. Results in an async _on_disconnect() call.
                print("DISCONNECTING")
                self._reset()
                return DisconnectResponse(
                    success=True, state=States.DISCONNECTED, message="Disconnected"
                )

            except Exception as e:
                print(f"Error in disconnect: {e}")
                return DisconnectResponse(
                    success=False,
                    state=self.state,
                    message=f"Error in disconnect: {e}",
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
            try:
                if self.configuration.callback_error:
                    raise InvalidConfigurationError()

                # Configuration is locally cached. If the network is down for a moment, can still get latest
                # if the client so desires.
                return GetConfigurationResponse(
                    success=True,
                    state=self.state,
                    message="Latest configuration provided",
                    configuration=self.configuration,
                )

            except Exception as e:
                return GetConfigurationResponse(
                    success=False,
                    state=self.state,
                    message=f"Latest valid configuration provided, but a more recent configuration was rejected",
                    configuration=self.configuration,
                    exception=e,
                )

    def report_status(self, status_payload: dict) -> ReportStatusResponse:
        """
        Report status to the host service:
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
                    print("ReportStatus throttled")
                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Throttled: too many requests",
                        exception=ClientAPIThrottle(details="Request: report_status"),
                    )

                try:
                    str_payload = json.dumps(status_payload)
                except Exception as e:
                    raise ReportStatusError(details=str(e)) from e

                print("Validating status payload")
                try:
                    validate(schema=self.schema, instance=status_payload)
                except Exception as e:
                    # This result will eventually feed into SDK Telemetry (WIP). Here the
                    # service will be informed about the error condition.
                    print(f"Invalid status payload: {e}")
                    return ReportStatusResponse(
                        success=False,
                        state=self.state,
                        message="Status Send Failed. Schema Validation Failure",
                        exception=InvalidStatusMessageError(details=str(e)),
                    )

                # QOS: 0 is best effort is sufficient for status messages that have a limited
                # value over time and need not be queued, accumulated and resent at a later time.
                try:

                    # Publish schema is attempted immediately on on_connect() callback.
                    # If that failed, we can try again here and if it fails again we can inform the client.
                    if not self._schema_delivered:
                        print("Attempting to re-publish schema")
                        self._report_schema()
                    try:

                        # This should never happen since the state must be CONNECTED.
                        topics = self.certs.get_topics()
                        if not topics or not self.mqtt_client:
                            raise ReportStatusError(
                                details="Skipping publish while not CONNECTED"
                            )

                        publish_message(
                            client=self.mqtt_client,
                            topic=topics.report_status,
                            payload=str_payload,
                            qos=0,
                            retain=False,
                        )
                        print("Status delivered")
                    except Exception as e:
                        raise ReportStatusError(details=str(e)) from e

                except Exception as e:
                    print(f"Can't publish status. Msg: {e}")
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
                print(f"Error in report_status: {e}")
                return ReportStatusResponse(
                    success=False,
                    state=self.state,
                    message=f"Status update not sent: {e}",
                    exception=e,
                )

    # PRIVATE METHODS ---------------------------------------------------

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

        # TODO: Handle revoked certs signalling the deregister and re-pairing should happen.
        #        Must inform the connect() client API about this event so the Response
        #        can include this in the Error().
        if reason_code in [mqtt.MQTT_ERR_NO_CONN, mqtt.MQTT_ERR_NO_CONN]:
            raise ConnectError(
                details=f"Credentials were refused or revoked. Deregister and re-pair"
            )

        if reason_code != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectError(
                details=f"Connection failed with result code {reason_code}"
            )

        print("ON CONNECT CALLBACK: code " + str(reason_code))
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
        print(f"MQTT Log: {level}: {buf}")

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
                device_id=self.certs.device_id,
            )

        if self.mqtt_client and self.state == States.CONNECTING:
            return ConnectResponse(success=True, state=self.state, message="Connecting")

        try:
            # State will remain CONNECTING until on_connect() callback.
            self._transition(States.CONNECTING)
            self.mqtt_client = mqtt.Client(
                client_id=self.certs.device_id,
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
                device_id=self.certs.device_id,
            )

        except Exception as e:
            print(f"Error in _start_connect: {e}")
            self._reset()

            # This is likely the most common error/exception encountered by the host application
            # as it is entirely possible for the users to initiate connections while the device
            # doesn't have an available network connection, is firewall blocked, etc.
            return ConnectResponse(
                success=False,
                state=self.state,
                message=f"Unable to connect at this time. Check network connection.",
                exception=ConnectError(
                    "Unable to make initial connection. Check network connection"
                ),
            )

    def _connect(self):
        ssl_context = ssl_alpn(
            ca_cert=self.certs.ca_cert_file,
            device_cert=self.certs.device_cert_file,
            private_key=self.certs.priv_key_file,
            iot_protocol_name=self.certs.host_settings.iot_protocol_name,
        )
        self.mqtt_client.tls_set_context(context=ssl_context)
        print(f"Connecting to: {self.certs.uri}")
        # Port 443 enables MQTT over HTTPs and transparency in most network environments.
        self.mqtt_client.connect(
            host=self.certs.uri,
            port=443,
            keepalive=self.certs.host_settings.mqtt_keepalive_seconds,
        )

    def _load_certs(self):
        return self.certs.read_from_filesystem()

    def _update_configuration_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the SUB_UPDATE_TOPIC persistent topic.
        An update here means the service just updated the configuration payload (or we just connected).
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
            print("Got a valid update config")
            # Increments the update_id and saves the payload.
            self.configuration.update_configuration(payload=config)
        except Exception as e:
            # Validation failure here can only happen if the service failed to validate.
            # Regardless, the SDK will perform its own validation here.

            # This is an asynchronous callback.
            # Persist the error in the Configuration class to inform the next get_configuration() Response.
            self.configuration.update_configuration(callback_error=True)
            raise InvalidConfigurationError(details=f"Schema Validation Error: {e}")

    def _update_certs_callback(self, client, userdata, message):
        """
        Called asynchronously in response to a new message received on the SUB_UPDATE_CERTS_TOPIC persistent topic.
        An update here means the service just updated the credentials payload (or we just connected).
        If different from the current device_cert, the client must immediately replace the device_cert, disconnect and
        reconnect.

        Args:
             client, userdata: unused metadata supplied by the mqtt client
             message: str device-cert PEM str format.

        Side Effect:
            Will result in a brief DISCONNECTED, CONNECTING state to any API call.

        """
        try:
            device_cert_pem_str = message.payload.decode("utf-8")
            assert device_cert_pem_str, "Empty cert provided by rotation."
            assert device_cert_pem_str.startswith(
                "-----BEGIN CERTIFICATE-----"
            ), "Invalid cert provided by rotation."
        except Exception as e:
            raise CertificatesRotationError(details="Msg: {e}.")

        try:
            with open(self.certs.device_cert_file, "r") as file:
                current_cert_pem_str = file.read()
                if device_cert_pem_str == current_cert_pem_str:
                    print("No change in device cert.")
                    return
                print("Updating device credentials")

                # Replace the device cert and disconnect/reconnect.
                self.certs.update_device_cert_file(device_cert_pem_str)
                host_id = self.host_id
                # Caller may see DISCONNECTED/CONNECTING while this processes...may take a few seconds.
                print(f"Momentarily reconnecting using new credentials.")
                self.disconnect()
                time.sleep(1)
                self.connect(host_id)

        except Exception as e:
            raise CertificatesRotationError(details="Msg: {e}.")

    def _report_schema(self):
        """
        Report the schema to the host service. Service might only accept this once per session.

        Raises:
            ConnectionError: For all MQTT publish error codes.
            ReportSchemaError
        """
        if not self._is(States.CONNECTED):
            print("Can't report schema when not connected")
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
        print("Reporting Schema")
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
        print("Schema delivered")

    def _is(self, state):
        # Differentiating CONNECTED from RECONNECTING is important to the client,
        # for all practical purposes the SDK state machine will treat them the same.
        if isinstance(state, list):
            return self.state in state
        return self.state == state

    def _transition(self, state):
        print(f"Setting state to {state}")
        self.state = state
