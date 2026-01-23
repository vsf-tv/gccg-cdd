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

from enum import Enum

class States(Enum):
    """
    SDK States
        DISCONNECTED = The SDK is quiet, not communicating to any host endpoint.
        PAIRING = The SDK has no credentials and is making API requests to the pairing and authenticate endpoints.
        CONNECTING = The SDK has credentials and starting or restarting an MQTT connection to the host=host_id
        CONNECTED = MQTT connection to the host=host_id is active
        RECONNECTING = The MQTT connection was dropped somehow.  SDK will attempt to reconnect until the client makes a
            disconnect() request.  Typically, this is a network outage.
    """
    DISCONNECTED = "DISCONNECTED"
    PAIRING = "PAIRING"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"

