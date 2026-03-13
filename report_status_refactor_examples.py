def _start_connect(self) -> ConnectResponse:
    """
    Attempts a connection once it has been determined a connection can happen: certs are available.

    Results:
        Response() returned directly by connect()

    """
    # Default success case
    success = True
    message = "Connection started"
    exception = None
    device_id = None
    region = None

    def check_already_connected():
        nonlocal success, message, device_id, region
        if self._is([States.RECONNECTING, States.CONNECTED]):
            success = True
            message = "Already connected or automatically re-connecting"
            device_id = self.certs.get_device_id()
            region = self.certs.get_region()
            return True
        return False

    def check_already_connecting():
        nonlocal success, message
        if self.mqtt_client and self.state == States.CONNECTING:
            success = True
            message = "Connecting"
            return True
        return False

    def perform_connection():
        nonlocal success, message, exception, device_id, region
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

            success = True
            message = "Connection started"
            region = self.certs.get_region()
            device_id = self.certs.get_device_id()

        except Exception as e:
            logger.exception(f"Error in _start_connect: {e}")
            self._reset()  # transitions to DISCONNECTED

            # This is likely the most common error/exception encountered by the host application
            # as it is entirely possible for the users to initiate connections while the device
            # doesn't have an available network connection, is firewall blocked, etc.
            success = False
            message = f"Unable to connect at this time. Check network connection."
            exception = ConnectError(
                "Unable to make initial connection. Check network connection"
            )

    # Execute logic
    if not (check_already_connected() or check_already_connecting()):
        perform_connection()

    return ConnectResponse(
        success=success,
        state=self.state,
        message=message,
        region=region,
        online_state=self.online_checker.get_online_state(),
        device_id=device_id,
        exception=exception
    )
