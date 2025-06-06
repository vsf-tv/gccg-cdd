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
from flask import Flask, request, jsonify
import fcntl
from typing import Optional
from discovery_sdk import CddSdk
import argparse
import signal
import sys


class CddSdkManager:
    """
    DSDK:  Discovery SDK Rest Client
    Usage: server_flask.py
                    --name <device_local_id (str)>
                    --certs_path <>
                    --schema_path <path>/instance_schema.json
                    --ip <eg. 127.0.0.1>
                    --port <port>

    The SDK host the following local endpoints for the client side API.
    - connect, disconnect, get_connection_state, report_status, get_configuration

    Example local endpoints requests:
    - curl -i -X GET http://0.0.0.0:8603/connect
    - curl -i -X GET http://0.0.0.0:8603/disconnect
    - curl -i -X GET http://0.0.0.0:8603/get_configuration
    - curl -i -X POST  -H "Content-Type: application/json" -d @/<path>/example_status.json  http://0.0.0.0:8603/report_status

    """

    _instance: Optional["CddSdkManager"] = None
    _DSDK_client = None

    def __init__(self, certs_path: str, device_local_id: str, schema_file: str, device_type: str):
        # If the SDK fails to load because the paths or schema file are bad, then an Exception will
        # be thrown here. These are indeed fatal errors and the application should not continue.

        if not CddSdkManager._instance:
            self._DSDK_client = CddSdk(
                certs_path=certs_path,
                device_local_id=device_local_id,
                schema_file=schema_file,
                device_type=device_type
            )
            CddSdkManager._instance = self

    @classmethod
    def get_instance(cls) -> "CddSdkManager":
        if not cls._instance:
            raise RuntimeError("DSDKManager not initialized")
        return cls._instance

    def get_client(self):
        return self._DSDK_client


class APIServer:
    def __init__(self, certs_path: str, device_local_id: str, schema_file: str, device_type: str):
        self.app = Flask(__name__)
        self.sdk_manager = CddSdkManager(
            certs_path=certs_path,
            device_local_id=device_local_id,
            schema_file=schema_file,
            device_type=device_type
        )
        self.setup_routes()

    def setup_routes(self):

        # Add after_request decorator to catch ALL responses.
        @self.app.after_request
        def after_request_func(response):
            return add_cors_headers(response)

        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type,Authorization"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

        @self.app.route("/connect", methods=["GET"])
        def connect():
            host_id = request.args.get('host_id')
            response = jsonify(self.sdk_manager.get_client().connect(host_id=host_id).to_dict())
            return response

        @self.app.route("/disconnect", methods=["GET"])
        def disconnect():
            return jsonify(self.sdk_manager.get_client().disconnect().to_dict())

        @self.app.route("/get_state", methods=["GET"])
        def get_connection_state():
            return jsonify(
                self.sdk_manager.get_client().get_connection_status().to_dict()
            )

        @self.app.route("/report_status", methods=["POST"])
        def report_status():
            payload = request.get_json()
            print(f"Got status payload.")
            return jsonify(
                self.sdk_manager.get_client()
                .report_status(status_payload=payload)
                .to_dict()
            )

        @self.app.route("/get_configuration", methods=["GET"])
        def get_configuration():
            return jsonify(self.sdk_manager.get_client().get_configuration().to_dict())


        @self.app.route("/deprovision", methods=["POST"])
        def deprovision():
            payload = request.get_json()
            force = payload.get("force", False)
            print(f"Force:", force)
            return jsonify(self.sdk_manager.get_client().deprovision(force=force).to_dict())

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port)


class ProcessAlreadyRunningError(Exception):
    """Raised when another instance of this process is already running"""
    pass


def ensure_single_instance():
    lock_file = "/tmp/your_program.lock"

    try:
        # Open the lock file.
        fp = open(lock_file, "w")
        # Try to get an exclusive lock.
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Keep the file pointer reference so the lock remains.
        return fp
    except IOError:
        print("Another instance is already running")
        raise ProcessAlreadyRunningError("Another instance is already running")


def main(device_local_id: str,
         certs_path: str,
         schema_file: str,
         tmp_path: str,
         ip: str,
         port: int,
         device_type: str):

    server = APIServer(
        certs_path=certs_path,
        device_local_id=device_local_id,
        schema_file=schema_file,
        device_type=device_type
    )

    def handle_exit(signum, frame):
        server.sdk_manager.get_client().disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    server.run(host=ip, port=port)


if __name__ == "__main__":
    """
    Starts the CDD SDK process. Once started the APIs can be accessed on the ip:port.

    Raises:
        RuntimeError: installation problem related to certs/schema paths.
        ProcessAlreadyRunningError: Only one SDK instance should be running.
    """

    # Prevents multiple instances of the SDK from running on one system.
    lock = ensure_single_instance()

    parser = argparse.ArgumentParser(
        description="Client Device Discovery",
        epilog="Documentation: https://github.com/vsf-tv/gccg-cdd/README.md",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--internal_device_id", required=True, type=str, help="Enter a device name")
    parser.add_argument(
        "--certs_path",
        required=True,
        type=str,
        help="Enter a path for persistent cert storage",
    )

    parser.add_argument(
        "--schema_path", required=True, type=str, help="Enter a path for the instance schema"
    )
    parser.add_argument(
        "--tmp_path",
        required=True,
        type=str,
        help="Enter a writable path for temporary storage",
    )
    parser.add_argument(
        "--ip",
        required=True,
        type=str,
        help="Enter an ip on which the SDK will host Rest APIs. Ideally you should run the server on"
             " 127.0.0.1 and access the SDK from a process running on the device. "
             " Using 0.0.0.0 makes the host available to external clients like Web Application running in a browser."
             " which may be convenient to integrate, but is risky in that it relies on network security for "
             " device-level access control.",
    )
    parser.add_argument(
        "--port",
        required=True,
        type=int,
        help="Enter a port on which the SDK will host Rest APIs.",
    )
    parser.add_argument(
        "--device_type",
        required=True,
        type=str,
        help="see MessageProtocol: SUPPORTED_DEVICE_TYPES eg. ENCODER|DECODER."
    )
    args = parser.parse_args()
    main(
        device_local_id=args.internal_device_id,
        certs_path=args.certs_path,
        schema_file=args.schema_path,
        tmp_path=args.tmp_path,
        ip=args.ip,
        port=args.port,
        device_type=args.device_type
    )
