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
import argparse
import fcntl
import os
import signal
import sys
from typing import Optional

# Third-party imports
from flask import Flask, jsonify, request

# Local application imports
from custom_logger import logger
from discovery_sdk import CddSdk


class CddSdkManager:
    """
    DSDK:  Discovery SDK Rest Client
    Usage: server_flask.py
                    --name <device_local_id (str)>
                    --certs_path <>
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

    def __init__(self, certs_path: str, device_local_id: str, device_type: str, log_path: str):
        # If the SDK fails to load because the paths or schema file are bad, then an Exception will
        # be thrown here. These are indeed fatal errors and the application should not continue.

        if not CddSdkManager._instance:
            self._DSDK_client = CddSdk(
                certs_path=certs_path,
                device_local_id=device_local_id,
                device_type=device_type,
                log_path=log_path,
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
    def __init__(self, certs_path: str, device_local_id: str, device_type: str, log_path: str):
        self.app = Flask(__name__)
        self.sdk_manager = CddSdkManager(
            certs_path=certs_path,
            device_local_id=device_local_id,
            device_type=device_type,
            log_path=log_path,
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
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,OPTIONS"
            return response

        @self.app.route("/connect", methods=["PUT"])
        def connect():
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            host_id = data.get('hostId') or data.get('host_id')
            registration = data.get('registration')
            if not host_id:
                return jsonify({"error": "host_id is required"}), 400
            response = jsonify(self.sdk_manager.get_client().connect(
                registration=registration, host_id=host_id
            ).to_dict())
            return response

        @self.app.route("/disconnect", methods=["PUT"])
        def disconnect():
            return jsonify(self.sdk_manager.get_client().disconnect().to_dict())

        @self.app.route("/get_state", methods=["GET"])
        def get_connection_state():
            return jsonify(
                self.sdk_manager.get_client().get_connection_status().to_dict()
            )

        @self.app.route("/report_status", methods=["PUT"])
        def report_status():
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            status = data.get('status')
            if not status:
                return jsonify({"error": "status is required"}), 400
            return jsonify(
                self.sdk_manager.get_client()
                .report_status(payload=status)
                .to_dict()
            )

        @self.app.route("/report_actual_configuration", methods=["PUT"])
        def report_configuration():
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            configuration = data.get('configuration')
            if not configuration:
                return jsonify({"error": "configuration is required"}), 400
            return jsonify(
                self.sdk_manager.get_client()
                .report_configuration(payload=configuration)
                .to_dict()
            )

        @self.app.route("/get_configuration", methods=["GET"])
        def get_configuration():
            return jsonify(self.sdk_manager.get_client().get_configuration().to_dict())

        @self.app.route("/deprovision", methods=["PUT"])
        def deprovision():
            host_id: str = request.args.get('host_id')
            if not host_id:
                return jsonify({"error": "host_id is required"}), 400
            force: bool = request.args.get('force', '').lower() in ('true', '1')
            return jsonify(
                self.sdk_manager.get_client().deprovision(
                    host_id=host_id,
                    force=force
                ).to_dict()
            )

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port)


class ProcessAlreadyRunningError(Exception):
    """Raised when another instance of this process is already running"""
    pass


def ensure_single_instance():
    lock_file = "/tmp/your_program.lock"
    
    try:
        # Open the lock file
        fp = open(lock_file, "w")
        # Try to get an exclusive lock (auto-releases when process dies)
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write PID for debugging
        fp.write(str(os.getpid()))
        fp.flush()
        # Keep the file pointer reference so the lock remains
        return fp
    except IOError:
        # Try to read the PID from the lock file
        try:
            with open(lock_file, "r") as f:
                existing_pid = f.read().strip()
            logger.error(f"Another instance is already running (PID: {existing_pid})")
            raise ProcessAlreadyRunningError(f"Another instance is already running (PID: {existing_pid})")
        except (FileNotFoundError, ValueError):
            logger.error("Another instance is already running")
            raise ProcessAlreadyRunningError("Another instance is already running")


def main(device_local_id: str,
         certs_path: str,
         tmp_path: str,
         log_path: str,
         ip: str,
         port: int,
         device_type: str
         ):

    server = APIServer(
        certs_path=certs_path,
        device_local_id=device_local_id,
        device_type=device_type,
        log_path=log_path
    )

    def handle_exit(signum, frame):
        server.sdk_manager.get_client().shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    server.run(host=ip, port=port)


if __name__ == "__main__":
    """
    Starts the CDD SDK process. Once started the APIs can be accessed on the ip:port.

    Raises:
        ProcessAlreadyRunningError: Only one SDK instance should be running.
    """

    # Prevents multiple instances of the SDK from running on one system.
    #lock = ensure_single_instance()

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
        "--tmp_path",
        required=True,
        type=str,
        help="Enter a writable path for temporary storage",
    )
    parser.add_argument(
        "--log_path",
        required=True,
        type=str,
        help="Enter a writable path for log storage",
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
        help="see MessageProtocol: SUPPORTED_DEVICE_TYPES eg. SOURCE|DESTINATION."
    )

    args = parser.parse_args()
    main(
        device_local_id=args.internal_device_id,
        certs_path=args.certs_path,
        tmp_path=args.tmp_path,
        log_path=args.log_path,
        ip=args.ip,
        port=args.port,
        device_type=args.device_type
    )
