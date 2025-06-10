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
import attr
from dataclasses import dataclass
from enum import Enum
import random
import string
from typing import Optional

# Simple UUID for the subscribed configuration update ID.
UPDATE_ID_SIZE = 5


class States(Enum):
    """
    SDK State machine
    """
    DISCONNECTED = "DISCONNECTED"
    PAIRING = "PAIRING"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"


class OnlineStates(Enum):
    """
    Online State machine
    """
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Configuration(object):
    """
    Maintains current service-supplied configuration payload and updates the update_id <str> to a new random value.
    Consumers can determine if a Configuration is new or already processed by comparing the current update_id
    to the update_id obtained in the previous call. The service has already validated the payload
    against the scoped-schema supplied on SDK start.
    """
    sequence: int = 0
    update_id: str = ""
    payload = {}
    callback_error: bool = False

    def update_configuration(self, payload: dict = {}, callback_error: bool = False):
        """
        Persists a new payload and updates the update_id.
        Called via the MQTT update call back.

        Args:
            payload (scoped-schema compliant configuration payload from service):
            callback_error: If True, do not update the configuration. Leave on the last good value.

        to_dict() Returns:
          {
            update_id = <str> A random string. Client must detect a change using !=
            payload = { < json conforming to the scoped schema > }
         }
        """

        # Persist any errors received updating the configuration.
        self.callback_error = callback_error

        # Leave the latest good configuration in place.
        if callback_error:
            print("Recording a configuration update failure")
            return

        self.sequence += 1
        base = "".join(random.choices(string.ascii_letters, k=UPDATE_ID_SIZE))
        self.update_id = f"{base}_{self.sequence}"
        self.payload = payload

        print(f"Updated configuration: {self.payload}")

    def to_dict(self) -> dict:
        return {"update_id": self.update_id, "payload": self.payload}


class Error(object):
    """
    Constructs an informative JSON model from an exception (see custom_exceptions).

    Args:
      exception: The underlying exception instance

    to_dict() Returns:
    {
        type:     The Exception Class Name, ex: SystemIntegrationError.
        message:  The default message for the exception type: exception.message.
        details:  An informative message unique to the exception instance: exception.details.
    }
    """
    def __init__(self, exception: Exception):
        self.type = exception.__class__.__name__
        self.message = exception.message if hasattr(exception, "message") else ""
        self.details = exception.details if hasattr(exception, "details") else ""

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "message": self.message,
            "details": self.details
        }


class Response(object):
    """
    Defines the SDK rest response model base class.

    Args:
        success: bool   Did the API succeed in its intended function or was there a problem.
        state: SDK State (see States).
        message: An informative message.
        exception: An exception encountered during the request handling.
    }
    """
    def __init__(
        self,
        success: bool = False,
        state: States = States.DISCONNECTED,
        message: str = "",
        exception: Optional[Exception] = None  # Will convert to an Error() class in the response message.
    ):
        self.success = success
        self.state = state
        self.message = message
        self.exception = exception

    def to_dict(self) -> dict:
        """
        Returns {
            "success": True|False,
            "state":   State() ENUM
            "message": "An informative message"
            "error": Error() Reports exceptions as an informative JSON model (see custom_exceptions)
                     The client application can decide which, if any, error attributes to display to
                     the user or simply retain for debug/logging.
            }
        """
        return {
            "success": self.success,
            "state": self.state.value,  # convert to str
            "message": self.message,
            "error": Error(self.exception).to_dict() if self.exception else None
        }


class ConnectResponse(Response):
    """
    Args:
        - Response base class attributes.
        - device_id, pairing_code, expires.
    """
    def __init__(
        self,
        success,
        state: States,
        message: str = "",
        online_state: Optional[OnlineStates] = None,
        exception: Optional[Exception] = None,
        device_id: str = "",
        region: str = "",
        pairing_code: str = "",
        expires: int = 0,
    ):
        super().__init__(success, state, message, exception)
        self.device_id = device_id
        self.pairing_code = pairing_code
        self.expires = expires
        self.online_state = online_state
        self.region = region

    def to_dict(self) -> dict:
        """
        Returns:
            {
             - Response base class attributes
             "device_id": <str>,
             "pairing_code": <str>, ~ 6 chars
             "expires": <int>,      minutes
            }
        """
        base_dict = super().to_dict()
        # Add the additional fields.
        base_dict.update(
            {
                "device_id": self.device_id,
                "pairing_code": self.pairing_code,
                "expires": self.expires,
                "online_state": self.online_state.value if self.online_state else None,
                "region": self.region,
            }
        )
        return base_dict


class DisconnectResponse(Response):
    pass

class DeprovisionResponse(Response):
    pass

class ReportStatusResponse(Response):
    pass


class GetConfigurationResponse(Response):
    """
    Args:
        - Response base class attributes.
        - configuration:  Configuration() class
    """
    def __init__(
        self,
        success: bool,
        state: States,
        message: str,
        exception: Optional[Exception] = None,
        configuration: Configuration = Configuration(),
    ):
        super().__init__(success, state, message, exception)
        self.configuration: Configuration = configuration

    def to_dict(self) -> dict:
        """
        Returns:
            {
             - Response base class attributes.
             "configuration": json (see Configuration() above
            }
        """
        base_dict: dict = super().to_dict()
        # Add the additional fields.
        base_dict.update({"configuration": self.configuration.to_dict()})
        return base_dict
