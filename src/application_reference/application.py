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
import argparse
from pathlib import Path
import threading
import time
import shutil
import signal
import subprocess
import os
import json
import requests
from requests.exceptions import Timeout

INITIAL_CONFIG_ID = ""  # identical to the SDK initial configuration update_id when no config has been obtained.


#  TODO: Status json is read from a file and only a few params are updated.  Make status update complete and
#    based on values from the underlying encoder/decoder/.  Possibly add RTP support.


# Client API endpoints.
PORT: int = 8603  # Ensure this matches the port used to start the discovery client SDK.
CONNECT = f"http://127.0.0.1:{PORT}/connect"
DISCONNECT = f"http://127.0.0.1:{PORT}/disconnect"
REPORT_STATUS = f"http://127.0.0.1:{PORT}/report_status"
GET_CONFIGURATION = f"http://127.0.0.1:{PORT}/get_configuration"
DEPROVISION = f"http://127.0.0.1:{PORT}/deprovision"

# From project source root.
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIGURATION_JSON_FILE = os.path.join(current_dir, "example_config.json")
STATUS_JSON_FILE = os.path.join(current_dir, "example_status.json")


def get_simulated_bitrate():
    """
    Returns a fake bitrate int between 20000 and 30000
    """
    return int((time.time() * 1000) % 10000) + 20000


class Encoder(object):
    """
    A basic FFMPEG encoder that will start/stop using the available webcam.

    Starts/Stops based on the srt_settings supplied by a schema compliant configuration.

    Note: Only handles SRT params (currently).
    """

    def __init__(self):
        self.process = None
        self.protocol = None
        self.srt_settings = None
        self.status_payload: dict = {}

    def running(self):
        # Carefully Start/Stop the ffmpeg encoder by monitoring the process. Don't want to start multiple.
        if self.process is None:
            return False
        return self.process.poll() is None

    def _update_encoder_config(self, updated_config: dict):
        self.config_payload = updated_config

    def get_encoder_status(self):
        """
        (Currently) This application reference design reads and makes minor changes to status that is read from a file.
        In practice, a real application should generate a complete status based on the current state.

        Returns:
            A instance-schema compliant status payload that represents the current encoder status.
        """

        with open(STATUS_JSON_FILE, "r") as f:
            self.status_payload = json.load(f)
            if not self.running():
                self.status_payload["status"]["channels"][0]["state"] = "IDLE"
                self.status_payload["status"]["channels"][0]["output_status"]["state"] = "IDLE"
                self.status_payload["status"]["channels"][0]["video_status"]["state"] = "IDLE"
                self.status_payload["status"]["channels"][0]["video_status"]["bitrate"] = 0
                self.status_payload["status"]["channels"][0]["audio_status"]["state"] = "IDLE"
            else:
                self.status_payload["status"]["channels"][0]["state"] = "ACTIVE"
                self.status_payload["status"]["channels"][0]["output_status"]["state"] = "ACTIVE"
                self.status_payload["status"]["channels"][0]["video_status"]["state"] = "ACTIVE"
                self.status_payload["status"]["channels"][0]["video_status"]["bitrate"] = get_simulated_bitrate()
                self.status_payload["status"]["channels"][0]["audio_status"]["state"] = "ACTIVE"
            return self.status_payload

    def start(self, str_settings: dict):

        # A client application should restart if params change while running.
        if not self.running():
            print(f"************* Starting *****************")
            ip = str_settings["ip"]
            port = str_settings["port"]
            stream_id = str_settings["stream_id"]
            cmd = f"ffmpeg -f avfoundation -framerate 30 -video_size 640x480 -i 0 -vcodec libx264 -f mpegts srt://{ip}:{port}/{stream_id}"
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

    def handle_update(self, update_message: dict):
        """
        Handles an update message from the underlying application.

        Args:
            update_message: A schema compliant configuration message.

        Note: This function comprehends the instance schema that it provided to the SDK on SDK Start.
               The SDK validated the service-provided configuration message conforms to the schema.
               As a result, we can confidently parse the configuration JSON here.
        """
        if not update_message:
            print("No update available")
            return

        print(f"Got an update: {update_message}")

        try:
            state = (
                update_message.get("configuration", {})
                .get("channels", [{}])[0]
                .get("state")
            )
            srt_settings = (
                update_message.get("configuration", {})
                .get("channels", [{}])[0]
                .get("output_configuration", {})
                .get("srt")
            )

            if state == "IDLE":
                print(f"Calling stop")
                self.stop()
            if state == "ACTIVE" and srt_settings:
                print(f"Calling Start")
                if self.running() and self.srt_settings == srt_settings:
                    print("Already running with same settings")
                    return  # No change, ignore

                # Stop then re-Start if the settings changed.
                if (
                    self.running()
                    and self.srt_settings
                    and self.srt_settings != srt_settings
                ):
                    self.stop()

                self.srt_settings = srt_settings
                self.start(srt_settings)

        except Exception as e:
            print(f"Unable to process command: {e}")


class ThumbnailSimulator(threading.Thread):
    """
    Given a source_dir with a bunch of images (all jpg or all png) copy to dest at the interval.
    The dest_dir must match the thumbnail_status from the instance schema and status message.

    In practice, the video encoder would be dumping images from the inputs and/or a decoder from the outputs.
    """
    def __init__(self, source_dir: str, dest: str, interval: int, name: str):
        super().__init__()
        self.valid = True
        self.source_dir = source_dir
        self.dest = dest
        self.dest_dir = os.path.dirname(dest)
        self.interval = interval
        self.files = [os.path.join(source_dir, f) for f in os.listdir(source_dir)]
        self.image_index = 0
        self.validate()
        self.temp_file = Path(dest).parent / f"temp_{name}"

    def validate(self):
        if not self.files:
            raise ValueError(f"No files found in source directory: {self.source_dir}")

        if not os.path.exists(self.source_dir):
            raise ValueError(f"Source directory does not exist: {self.source_dir}")

        if not os.path.exists(self.dest_dir):
            raise ValueError(f"Destination directory does not exist: {self.dest_dir}")

        if not os.access(self.dest_dir, os.W_OK):
            raise ValueError(f"Destination directory is not writable: {self.dest_dir}")

    def pick_image(self) -> str:
        # cycle through all images in source_dir infinitely
        image_path = self.files[self.image_index]
        self.image_index += 1
        if self.image_index >= len(self.files):
            self.image_index = 0
        return image_path

    def stop(self):
        self.valid = False

    def run(self):
        while self.valid:
            image = self.pick_image()
            try:
                # shutil.copy mimics non-atomic (chunked) writes typical for an encoder emitting a Thumbnail.
                # If transmitted, may result in send a partial file.
                shutil.copy2(src=image, dst=self.temp_file)
                # After the imagee is emitted by the 'encoder' (simulated above),
                # move performs an atomic copy operation so self.dest is always a complete file.
                shutil.move(self.temp_file, self.dest)
                # Ensures the file mtime is updated which is essential for stale file detection!
                Path(self.dest).touch()
            except Exception as e:
                # Clean up the temp file if something goes wrong
                print(f"Error writing TN image to disk: msg {e}")
                os.unlink(self.temp_file)
            time.sleep(self.interval)


class ClientApplication(object):
    """
    A basic client application that will start/stop using the available webcam.
    """

    def __init__(self):
        self.encoder = Encoder()
        self.running = True
        self.latest_configuration_id = INITIAL_CONFIG_ID
        self.current_configuration: dict = {}
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.thumbnail_emitter_sdi = ThumbnailSimulator(
            source_dir=os.path.join(Path(__file__).parent, "thumbnail_images_sdi"),
            dest="/tmp/image_sdi.jpg",  # Matches schema and status message
            interval=2,
            name="sdi"
        )
        self.thumbnail_emitter_hdmi = ThumbnailSimulator(
            source_dir=os.path.join(Path(__file__).parent, "thumbnail_images_hdmi"),
            dest="/tmp/image_hdmi.jpg",  # Matches schema and status message
            interval=2,
            name="hdmi"
        )

    def signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully.
        Applications should make disconnect() request when they close inform the service the client has gone away.
        Alternatively, shutting down the client process will attempt to inform the service in it shutdown hanlder.
        """
        print("Received shutdown signal, cleaning up...")
        response = requests.get(DISCONNECT, timeout=1)
        self.running = False

    def report_status(self):
        """
        Report the current state of the system and the ffmpeg encoder.
        TODO:  This application will provide a complete status based on the actual application status.
        """
        status_payload = self.encoder.get_encoder_status() | self.current_configuration
        response = requests.post(REPORT_STATUS, json=status_payload, timeout=5)
        if response.status_code == 200:
            sdk_response = parse_api_response(response)
            print(
                f"report_status Success: {sdk_response.get('success')}  State: {sdk_response.get('state')}"
                f" error: {sdk_response.get('error')} DeviceID: {sdk_response.get('device_id')}"
                f" message: {sdk_response.get('message')}"
            )

    def get_configuration(self):
        """
        Obtains a configuration message.
        Checks if the update_id changed, if so applies the change, otherwise ignores.
        """
        response = requests.get(GET_CONFIGURATION, timeout=5)
        if response.status_code == 200:
            sdk_response = parse_api_response(response)
            print(
                f"get_configuration Success: {sdk_response.get('success')} State: {sdk_response.get('state')}"
                f" error: {sdk_response.get('error')} DeviceID: {sdk_response.get('device_id')}"
                f" message: {sdk_response.get('message')} configuration: {sdk_response.get('configuration')}"
            )
            # See: get_configuration() response.
            configuration: dict = sdk_response.get("configuration", {})
            update_id: str = configuration.get("update_id", "")
            configuration_payload: dict = configuration.get("payload", {})
            # ID is an arbitrary string. Check for a difference.
            # If there is no change (ie already processed based on the ID) then do nothing
            # because we've already processed this configuration.
            if update_id != self.latest_configuration_id:
                print(f"New update. update_id: {update_id}")
                self.latest_configuration_id = update_id
                self.encoder.handle_update(configuration_payload)

                # This simple reference design application simply reflects the host-service-provided 'desired'
                # configuration back to the host service as the 'actual' configuration. In real application,
                # a local user might override one or more settings or for some reason be unable to comply with
                # (part of) the desired configuration.  The application reports status and current configuration
                # via the report_status() API.
                # See: Host Service API: configuration: desired/actual.
                self.current_configuration = configuration_payload

    def run_loop(self, host_id: str):
        """
        Guidance for client applications: (see: documentation: SDK API, SDK Reference Design).

        connect() API
            Response(state)
            PAIRING: Display state and Display pairing_code to the user.
            CONNECTING: Display state to the user. The SDK is attempting to connect,
                        if the network is open, usually takes < 1s.
            CONNECTED:  Display state to the user. The SDK is connected to the service
                        and operating normally. Calling connect() while already CONNECTED is a
                        valid approach and can simplify client application logic.
            DISCONNECTED: Display state to the user. See: Handling Revoked or Expired Certs below.

            Response(online_state)
            ONLINE: Response to Port 443/https GET request on one of the URls provided in the host_config was
                    successful. Indicates network environment is suitable for pairing and MQTT connections.
            OFFLINE: Connection to pairing and MQTT endpoints is not possible at this time.

            Response(success)
            Bool:  True | False
            Indicates the request was fully processed, no exceptions raised.

            Response(message)
            <str>
            An informative message about the success/failure of the request.

            Response(pairing_code)
            <str>
            Present if: Response(state) == PAIRING

            Response(expires)
            <int> seconds
            Present if: Response(state) == PAIRING
            Indicates the time until the pairing_code will expire, after which a subsequent call to connect()
            will automatically restart the pairing process and result in Response(state) == PAIRING and
            an updated Response(expires)



        Application Guidance: Run Loop
            loop over connect() until Response(state)=CONNECTED(),
            then loop over get_configuration(), report_status(),

            Note: Each report_status() request invokes a validation and MQTT publish which requires processing by the
            SDK and host service.  Host_Settings(min_interval_pub_seconds)   (See Host Service API)  indicates the max
            publish rate beyond which messages will be throttled by the SDK automatically and/or host_service if the
            SDK throttling is somehow disabled.  Applications should be mindful of excessive publish that can
            incur throttling and/or possibly disconnects as a result of violating min_interval_pub_seconds limit.

            Note: report_status() should only when something interesting has changed on the device.
            Consider that minor differences like a small bitrate change is probably not worth reporting.

        Application Guidance: Handling Revoked or Expired Certs:

            This is indicated by *persistent* Response(state) == CONNECTING or RECONNETING and
            Response(online_state) == ONLINE.  This means the client is able to reach the public internet
            (ONLINE) but can not establish a connection to the service.  The Host API does not provide a definitive
            means by which a client can disambiguate an outage on the MQTT broker and expired/deprovisioned credentials.
            MQTT broker endpoints fortunately are generally very resilient with ample redundancy and failover.

            What an application should do:
            1) Inform the user the client the device is online but a connection is not established
            2) Inform the user to invoke deprovision and re-pair the device.

            An application SHOULD NOT automatically deprovision and repair as user-involvement is required to
            re-pair the device.
        """
        self.thumbnail_emitter_sdi.start()
        self.thumbnail_emitter_hdmi.start()
        failed_connect_attempts_while_online: int = 0
        while self.running:
            try:
                print("........................")
                response = requests.get(CONNECT, params={"host_id": host_id}, timeout=5)
                if response.status_code == 200:
                    sdk_response = parse_api_response(response)
                    online = sdk_response.get('online_state')
                    state = sdk_response.get('state')
                    print(
                        f"run_loop Success: {sdk_response.get('success')} State: {state} "
                        f"online: {online} "
                        f" error: {sdk_response.get('error')} DeviceID: {sdk_response.get('device_id')} "
                        f" message: {sdk_response.get('message')}."
                    )

                    #
                    # PAIRING: If the SDK returns PAIRING then present the pairing_code to the user so the device
                    #          can be claimed in the service.
                    #
                    if (
                        sdk_response.get("success")
                        and state == "PAIRING"  # see (SDK models)
                    ):
                        print(
                            f"Device is not paired. Pairing Code: {sdk_response.get('pairing_code')} Expires in: {sdk_response.get('expires')}s."
                        )

                    #
                    # Possibly the client has been deprovisioned or certs have expired.
                    #
                    if state in ["DISCONNECTED", "CONNECTING"]:
                        if online == "ONLINE":
                            print(f"Unable to connect to the service, but the device is online. "
                                  f"Likely, the certs have expired or the device has been deprovisioned.",
                                  f"Consider, deprovision and re-pairing.")
                            failed_connect_attempts_while_online += 1
                            # Persistent in this case is about 30 seconds ( 10 tries x 3s interval )
                            if failed_connect_attempts_while_online > 10:
                                print("Too many failed connect attempts. Deprovisioning...")
                                requests.post(DEPROVISION, params={"host_id": host_id, 'force': True}, timeout=5)
                                self.running = False
                                break

                        elif online == "OFFLINE":
                            print(f"Device is offline, unable to reach the internet and "
                                  f"will be unable to connect until the network connection is restored.")

                    #
                    # CONNECTED: send any status update, check for an updated configuration.
                    #
                    if sdk_response.get("success") and state in [
                        "CONNECTED"
                    ]:  # See (SDK models.py).
                        # The service will respond for any state but best to only call these when the SDK is CONNECTED
                        # so that messages sent/received are handled and current.
                        failed_connect_attempts_while_online = 0
                        self.get_configuration()
                        self.report_status()

                else:
                    print(f"Connection failed. Status code: {response.status_code}")
            except Timeout:
                print("Connection timed out. Retrying...")
            except Exception as e:
                print(f"An error occurred: {e}")

            # Simulate producing a thumbnail image.  Copy from the SDK repository to the thumbnail directory
            # advertised in the instance schema.
            time.sleep(3)

        self.thumbnail_emitter_sdi.stop()
        self.thumbnail_emitter_hdmi.stop()
        print("Exiting")


def parse_api_response(response) -> dict:

    resp = json.loads(response.content.decode("utf-8"))
    return resp


def main(host_id: str):
    c = ClientApplication()
    print(f"Connecting to: {host_id}")
    c.run_loop(host_id=host_id)


if __name__ == "__main__":
    """
    Starts the application reference design program. Expects a client SDK process to be running already.
    Communicates with that process via the client SDK API.
    """
    parser = argparse.ArgumentParser(
        description="Client Device Discovery Application Reference Design",
        epilog="Documentation: https://github.com/vsf-tv/gccg-cdd/README.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host_id", required=True, type=str, help="Enter a host_id to connect"
    )
    args = parser.parse_args()

    main(host_id=args.host_id)
