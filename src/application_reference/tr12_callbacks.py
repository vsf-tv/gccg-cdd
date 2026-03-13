"""
TR-12 Callback implementations for testing the Tr12Shim.

Update callbacks print the received values.
Get callbacks return stub values based on the 1-channel encoder registration.

Keys used in callbacks match Setting.name from registration.json (BUG WORKAROUND):
  Device-level: "Clock Source"
  Channel-level: "resolution", "framerate", "max_bitrate", "rate_control", "codec", "gop_size", "selected_input"
"""

from typing import Optional

from cdd_sdk_client.models.connection import Connection
from cdd_sdk_client.models.srt_caller import SrtCaller
from cdd_sdk_client.models.srt_caller_transport_protocol import SrtCallerTransportProtocol
from cdd_sdk_client.models.transport_protocol import TransportProtocol
from cdd_sdk_client.models.channel_state import ChannelState

from application_reference.simple_encoder import Encoder


class Callbacks:
    """Callback implementations for Tr12Shim."""

    def __init__(self):
        # This is a simple ffmpeg encoder running locally.   Not all registered settings are necessarily implemented (yet)
        self.encoder = Encoder()

    # --- Update callbacks (print statements) ---

    def update_device_key_value(self, key: str, value: str) -> None:
        print(f"[UPDATE] Device setting: {key} = {value}")

    def update_channel_settings(self, channel_id: str, key: str, value: str) -> None:
        print(f"[UPDATE] Channel {channel_id} setting: {key} = {value}")

    def update_channel_profile(self, channel_id: str, profile_id: str) -> None:
        print(f"[UPDATE] Channel {channel_id} profile: {profile_id}")

    def update_channel_connection(self, channel_id: str, connection: Connection) -> None:
        print(f"[UPDATE] Channel {channel_id} connection: {connection}")
        self.encoder.handle_transport_configuration_change(channel_id, connection)

    def update_channel_state(self, channel_id: str, state: ChannelState) -> None:
        print(f"[UPDATE] Channel {channel_id} state: {state}")
        """
        It is VERY VERY important to understand that TR-12 communicate a desired configuration once.
        The client will report actual configuration, so if the device is unably to comply the host 
        will be thus informed.  However, it is still the responsibility of the device to keep trying. 
        For example, in this callback, state = ACTIVE, the device might not currently be able to actually 
        start...for example the receiver is not available.  In this case, is the device's responsibility to 
        perform "retires" according to the last received configuration. 
        The TR-12 Host is NOT responsible for re-configuring the device again and again
        until the desired state is achieved.  Simply failing with a error message
        might be how your device's native console works, but that is not "TR-12" compliant.
        
        This applies to ALL settings.  This is called out here since start/stop failures are far more common
        than other configuration problems.
        
        """
        # TODO: Implement retires in the Encoder() class.  This ARD doesn't currently do handle them
        self.encoder.handle_update_state(channel_id, state)

    # --- Get callbacks (stub values from registration defaults) ---
    # Keys are Setting.name values from registration.json (BUG WORKAROUND)

    def get_device_updated_value(self, key: str) -> Optional[str]:
        """Return stub device-level setting values.
        
        Device settings from registration:
          - id: "sync_clock_source", name: "Clock Source", default: "NTP"
        """
        defaults = {
            "sync_clock_source": "NTP",
        }
        return defaults.get(key)

    def get_channel_updated_value(self, channel_id: str, key: str) -> Optional[str]:
        """Return stub channel setting values.
        
        # BUG WORKAROUND: Host service currently sends Setting.name as the key
        # instead of Setting.id. Using name values until host service is fixed.
        # Correct keys should be: RS01, FR01, MB01, RC01, CO01, GP01, IN01
        
        Channel settings from registration (name -> default):
          - resolution: "1920x1080"
          - framerate: "30"
          - max_bitrate: "10000"
          - rate_control: "CBR"
          - codec: "H.264"
          - gop_size: "60"
          - selected_input: "SDI1"
        """
        # BUG WORKAROUND: Using Setting.name instead of Setting.id
        defaults = {
            "resolution": "1920x1080",
            "framerate": "30",
            "max_bitrate": "10000",
            "rate_control": "CBR",
            "codec": "H.264",
            "gop_size": "60",
            "selected_input": "SDI1",
        }
        return defaults.get(key)

    def get_channel_profile_value(self, channel_id: str) -> Optional[str]:
        """Return stub profile ID.
        
        Available profiles from registration:
          - h264c, h264f, h265c, h265k
        
        Return None to use simple_settings instead of profile.
        """
        return None  # Use simple settings by default

    def get_channel_connection(self, channel_id: str) -> Optional[Connection]:
        """Return a stub SRT caller connection (matches SRT_CALLER from registration)."""
        srt_caller_protocol = SrtCallerTransportProtocol(
            stream_id="test_stream",
            ip="127.0.0.1",
            port=5000,
            minimum_latency_milliseconds=200
        )
        return Connection(
            transport_protocol=TransportProtocol(
                actual_instance=SrtCaller(srt_caller=srt_caller_protocol)
            )
        )

    def get_channel_state(self, channel_id: str) -> ChannelState:
        """Return channel state as string (ACTIVE/IDLE)."""
        return self.encoder.get_channel_state(channel_id)

    def get_device_status(self) -> list[dict]:
        """Return device-level status (cpu, temp)."""
        if self.encoder.running():
            return [
                {
                    'name': 'cpu',
                    'value': '61',
                    'info': 'Current CPU % utilization.'
                 },
                {
                    'name': 'temp',
                    'value': '84',
                    'info': 'CPU in degrees C.'
                },
                {
                    "name": "model",
                    "value": "Talon",
                    "info": "Hardware device model identifier."
                },
                {
                    "name": "serial",
                    "value": "123456789",
                    "info": "Device serial number."
                }
            ]
        return [
            {
                'name': 'cpu',
                'value': '31',
                'info': 'Current CPU % utilization.'
            },
            {
                'name': 'temp',
                'value': '76',
                'info': 'CPU in degrees C.'
            },
            {
                "name": "model",
                "value": "Talon",
                "info": "Hardware device model identifier."
            },
            {
                "name": "serial",
                "value": "123456789",
                "info": "Device serial number."
            }
        ]

    def get_channel_status(self, channel_id: str) -> list[dict]:
        """Return channel-level status (bitrate)."""
        from application_reference.simple_encoder import get_simulated_bitrate
        if self.encoder.running():
            return [
                {'name': 'bitrate', 'value': get_simulated_bitrate(), 'info': 'Bitrate Mbps configured on the video encoder.'}
            ]
        return [
            {'name': 'bitrate', 'value': '0', 'info': 'Bitrate Mbps configured on the video encoder.'}
        ]

