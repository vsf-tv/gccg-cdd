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

import os
import signal
import subprocess
import time
from typing import Optional

FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"

from openapi_client.models.srt_caller_transport_protocol import SrtCallerTransportProtocol
from openapi_client.models.channel_state import ChannelState
from openapi_client.models.connection import Connection

def get_simulated_bitrate() -> str:
    """
    Returns a fake bitrate int between 20000 and 30000
    """
    return str(int((time.time() * 1000) % 10000) + 20000)


class Encoder(object):
    """
    A basic FFMPEG encoder that will start/stop using the available webcam.
    Note: Only handles SRT params (currently).
    """

    def __init__(self):
        self.process = None
        self.protocol = None
        self.srt_settings = None
        self.status_payload: dict = {}
        self.srt_config_settings: Optional[SrtCallerTransportProtocol] = None

    def running(self):
        # Carefully Start/Stop the ffmpeg encoder by monitoring the process. Don't want to start multiple.
        if self.process is None:
            return False
        return self.process.poll() is None

    def _update_encoder_config(self, updated_config: dict):
        self.config_payload = updated_config

    def get_channel_state(self, channel: str) -> ChannelState:
        return ChannelState.ACTIVE if self.running() else ChannelState.IDLE

    def start(self, str_settings: SrtCallerTransportProtocol):

        # A client application should restart if params change while running.
        if not self.running():
            print(f"************* Starting *****************")
            ip = str_settings.ip
            port = str_settings.port
            stream_id = str_settings.stream_id
            cmd = (f"{FFMPEG_PATH} -f avfoundation -framerate 30 -video_size 640x480 "
                   f"-i 0 -vcodec libx264 -f mpegts srt://{ip}:{port}/{stream_id}")
            print(f"command: {cmd}")
            self.process = subprocess.Popen(
                cmd, shell=True, preexec_fn=os.setsid
            )  # Detach from parent.
        else:
            print("Already running")

    def stop(self):

        print("************* Stopping *****************")

        if (
            self.process is not None and self.process.poll() is None
        ):  # Check if process is still running.
            try:
                # First try SIGINT (Ctrl+C)
                self.process.send_signal(signal.SIGINT)
                print(f"Sent SIGINT signal to process {self.process.pid}")

                # Wait for a short time to see if the process exits.
                try:
                    self.process.wait(timeout=5)  # Wait up to 5 seconds.
                except subprocess.TimeoutExpired:
                    # If SIGINT didn't work, try SIGTERM.
                    print(f"Process didn't respond to SIGINT, trying SIGTERM...")
                    self.process.send_signal(signal.SIGTERM)

                    try:
                        self.process.wait(timeout=5)  # Wait again for SIGTERM.
                    except subprocess.TimeoutExpired:
                        print(f"Process didn't respond to SIGTERM either")
                        # Optionally, you could use SIGKILL as a last resort.
                        # self.process.kill()  # This is equivalent to SIGKILL.

                self.process = None

            except ProcessLookupError:
                print(f"Process {self.process.pid} may have already terminated.")

        else:
            print("Already stopped")

    def handle_transport_configuration_change(self, channel, connection: Connection):
        """
        Handles a transport configuration change message from the underlying application.

        Args:
            :param channel:  the channel id
            :param connection: the Connection object containing the transport protocol details
        """
        self.srt_config_settings = connection.transport_protocol.actual_instance
        if not isinstance(self.srt_config_settings, SrtCallerTransportProtocol):
            print(f"Unsupported transport protocol: {type(self.srt_config_settings)}")
            return
        if self.srt_config_settings:
            print(f"Got an update: {self.srt_config_settings.to_json()}")
        else:
            print("Got a null SRT config update - stopping encoder")
            self.stop()

    def handle_update_state(self, channel: str, state: str) -> bool:
        """
        Handles a device configuration change message from the underlying application.
        Args:
            :param channel: the channel id
            :param state: the Connection object containing the transport protocol details
        """
        try:
            if state == ChannelState.IDLE:
                print(f"Calling stop")
                self.stop()
                return True
            if state == ChannelState.ACTIVE:
                if hasattr(self.srt_config_settings, 'srt_caller'):
                    print(f"Calling Start")
                    if self.running() and self.srt_config_settings.srt_caller == self.srt_settings:
                        print("Already running with same settings (ip at least)")
                        return True

                    # Stop then re-Start if the settings changed.
                    if (
                        self.running()
                        and self.srt_settings
                        and self.srt_settings != self.srt_config_settings.srt_caller
                    ):
                        self.stop()

                    self.srt_settings = self.srt_config_settings.srt_caller
                    self.start(self.srt_config_settings.srt_caller)


        except Exception as e:
            print(f"Unable to process command: {e}")

        return True
