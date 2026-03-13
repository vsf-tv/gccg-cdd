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
import os
import json
from requests.exceptions import Timeout
from typing import Optional

from cdd_sdk_client import Configuration, ApiClient
from cdd_sdk_client.api.default_api import DefaultApi
from cdd_sdk_client.models.connect_request_content import ConnectRequestContent
from cdd_sdk_client.models.connect_response_content import ConnectResponseContent
from cdd_sdk_client.models.device_registration import DeviceRegistration
from cdd_sdk_client.models.report_status_request_content import ReportStatusRequestContent
from cdd_sdk_client.models.report_status_response_content import ReportStatusResponseContent
from cdd_sdk_client.models.device_status import DeviceStatus
from cdd_sdk_client.models.report_actual_configuration_request_content import ReportActualConfigurationRequestContent
from cdd_sdk_client.models.device_configuration import DeviceConfiguration
from cdd_sdk_client.models.get_configuration_response_content import GetConfigurationResponseContent

from application_reference.tr12_shim import Tr12Shim
from application_reference.tr12_callbacks import Callbacks

INITIAL_CONFIG_ID = ""  # identical to the SDK initial configuration update_id when no config has been obtained.

#  TODO: Status json is read from the payloads/status.sjon file
#   Only a few params are updated.
#   Make status update based on values from the underlying encoder/decoder/.

# TR-12 Client API endpoints.
PORT: int = 8603

# Configure API client SDK auto generated from the smithy cdd_sdk definitions.
api_configuration = Configuration(host=f"http://127.0.0.1:{PORT}")
api_client = ApiClient(api_configuration)
api_instance = DefaultApi(api_client)

# From project source root.
current_dir = Path(os.path.abspath(__file__)).parent
payloads_dir = Path(current_dir).parent / "payloads"

# Your device should have its own Registration file
REGISTRATION_JSON_FILE = payloads_dir / "1_channel_encoder" / "registration.json"

class ThumbnailSimulator(threading.Thread):
    """
    Given a source_dir with a bunch of images (all jpg or all png) copy to dest at the interval.
    The dest_dir must match the thumbnail payload from the registration file and status message.

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
        self.shim = Tr12Shim(Callbacks())
        self.encoder = self.shim.callbacks.encoder
        self.running = True
        self.latest_configuration_id = INITIAL_CONFIG_ID
        self.current_configuration: Optional[DeviceConfiguration] = None
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.thumbnail_emitter_sdi = ThumbnailSimulator(
            source_dir=os.path.join(Path(__file__).parent, "thumbnail_images_sdi"),
            dest="/tmp/image_sdi.jpg", # See Registration Schema
            interval=2,
            name="sdi"
        )
        self.thumbnail_emitter_hdmi = ThumbnailSimulator(
            source_dir=os.path.join(Path(__file__).parent, "thumbnail_images_hdmi"),
            dest="/tmp/image_hdmi.jpg",
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
        try:
            api_instance.disconnect()
        except Exception as e:
            print(f"Error during disconnect: {e}")
        self.running = False

    def report_status(self):
        """
        Report the current state of the system and the ffmpeg encoder.
        Makes a report_status request passing ReportStatusRequestContent()
        TR12 API
        """
        device_status: DeviceStatus =  self.shim.get_device_status()
        req = ReportStatusRequestContent.from_dict({
            "status": device_status.to_dict()
        })
        response: ReportStatusResponseContent = api_instance.report_status(report_status_request_content=req.to_dict())
        
        print(
            f"report_status Success: {response.success}  State: {response.state}"
            f" error: {response.error}  message: {response.message}"
        )

    def report_actual_configuration(self):
        """
        Makes a report_actual_configuration request passing the ReportActualConfigurationRequestContent

        Reports the actual configuration of the system.  This function informs the
        service about the complete, current state of the encoder device.

        The CDD Protocol explicitly requires the client apply all desired configuration params
        and disallow local overrides while connected.

        The host service will treat all differences as:
        1. The device is offline
        2. The desired configuration is being applied but hasn't yet (control latency)
        3  A Error: the device is unable to accept the configuration.

        Host service will not want to assume any responsibility for (3) since practically there is
        nothing to be done as this is a device control plane defect.

        """

        # For this simple example application: we will just reflect the desired back.  An actual device
        # should create a complete configuration payload from the current state of the device config.
        if not self.current_configuration:
            print("No configuration to report")
            return

        req: ReportActualConfigurationRequestContent = ReportActualConfigurationRequestContent.from_dict({
            "configuration": self.current_configuration.to_dict()
        })
        response = api_instance.report_actual_configuration(report_actual_configuration_request_content=req.to_dict())
        
        print(
            f"report_actual_configuration Success: {response.success}  State: {response.state}"
            f" error: {response.error}  message: {response.message}"
        )

    def get_configuration(self) -> str:
        """
        makes a get_configuration request passing the GetConfigurationResponseContent

        Gets the latest configuration message.
        Checks if the update_id changed, if so applies the change, otherwise ignores.
        """
        response: GetConfigurationResponseContent = api_instance.get_configuration()
        update_id: str = ""
        
        print(
            f"get_configuration Success: {response.success} State: {response.state}"
            f" error: {response.error}"
            f" message: {response.message} configuration: {response.configuration}"
        )
        
        if response.configuration:
            update_id = response.configuration.update_id
            device_configuration: DeviceConfiguration = response.configuration.payload
            
            # ID is an arbitrary string. Check for a difference.
            # If there is no change (ie already processed based on the ID) then do nothing
            # because we've already processed this configuration.
            if update_id != self.latest_configuration_id:
                print(f"New update. update_id: {update_id}")
                self.latest_configuration_id = update_id

                # Test shim apply_desired_configuration
                print(f"[SHIM TEST] apply_desired_configuration.")
                success = self.shim.apply_desired_configuration(device_configuration)

                # This reference design application simply reflects the host-service-provided 'desired'
                # configuration back to the host service as the 'actual' configuration. In real application,
                # a local user might override one or more settings or for some reason be unable to comply with
                # (part of) the desired configuration.  The application reports status and current configuration
                # via the report_status() API.
                # See: Host Service API: configuration: desired/actual.
                if success:
                    self.current_configuration = device_configuration
                    # Test shim get_actual_configuration
                    with open(REGISTRATION_JSON_FILE, "r") as f:
                        reg = DeviceRegistration.from_dict(json.load(f))
                    actual_config = self.shim.get_actual_configuration(reg)
                    print(f"[SHIM TEST] get_actual_configuration: {actual_config.to_json()}")

        return update_id

    def run_loop(self, registration_dict: dict, host_id: str):
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

            The client SDK when connected will acknowledge a deprovisioned device, and remove certs locally. If
            deprovisioned while offline, the device will perform this on the next connection to that host.

            A client calling connect() after deprovision has processed will simply re-enter the pairing state.
        """
        self.thumbnail_emitter_sdi.start()
        self.thumbnail_emitter_hdmi.start()
        registration_payload: DeviceRegistration = DeviceRegistration.from_dict(registration_dict)
        while self.running:
            try:
                print(f"........................")

                # First, try to connect using certs the SDK should locate based on the host_id.
                req: ConnectRequestContent = ConnectRequestContent.from_dict({
                    "registration": registration_payload.to_dict(),
                    "hostId": host_id
                })
                resp: ConnectResponseContent = api_instance.connect(connect_request_content=req.to_dict())
                print(
                    f"Success: {resp.success} State: {resp.state} "
                    f" error: {resp.error} DeviceID: {resp.device_id} "
                    f" message: {resp.message}."
                )

                # PAIRING: response.state == 'PAIRING' then:
                # Present the pairing_code to the device user to they can communicate it to the host service
                # to be claimed.
                if resp.success and resp.state == "PAIRING":
                    print(
                        f"Device is not paired. Pairing Code: {resp.pairing_code} Expires in: {resp.expires}s."
                    )

                #
                # While CONNECTED: Send a status update, check for an updated configuration.
                #
                if resp.success and resp.state == "CONNECTED":
                    # The service will respond for any state but best to only call these when the SDK is CONNECTED
                    # so that messages sent/received are handled and current.
                    update_id = self.get_configuration()

                    # Be careful here...the SDK and Service will throttle if you exceed pub limits.
                    # This application calls pub every 3 seconds, which requires a host min pub interval < 3s
                    # The VSF test host min pub interval is 5s.
                    # This application will only call report_status() when something interesting has changed.
                    # Consider that minor differences like a small temp/bitrate change is probably not worth reporting.
                    # See: report_status() API guidance.
                    self.report_status()
                    self.report_actual_configuration()

            except Timeout:
                print("Connection timed out. Retrying...")
            except Exception as e:
                print(f"An error occurred: {e}")

            # Simulate producing a thumbnail image.  Copy from the SDK repository to the thumbnail directory
            # advertised in the registration file.
            time.sleep(3)

        self.thumbnail_emitter_sdi.stop()
        self.thumbnail_emitter_hdmi.stop()
        print("Exiting")


def parse_api_response(response) -> dict:

    resp = json.loads(response.content.decode("utf-8"))
    return resp


def main(host_id: str):
    with open(REGISTRATION_JSON_FILE, "r") as f:
        registration_dict = json.load(f)
        c = ClientApplication()
        print(f"Connecting to: {host_id}")
        c.run_loop(registration_dict=registration_dict, host_id=host_id)


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
