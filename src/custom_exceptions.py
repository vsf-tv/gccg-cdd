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


"""
    Defines all SDK raised Exceptions.

    The SDK can raise exceptions at any level of the call stack.
    The API handler catches and includes these exceptions in the Response "error".
    see (models: Response() and Error())

"""


class SDKBaseException(Exception):
    """
    Base exception for all Discovery SDK errors.

    Args:
      details: An informative message unique to the exception instance.

    Attributes:
        message: The default message for the exception type.
        details: An informative message unique to the exception instance.

    """

    def __init__(self, message, details=""):
        super().__init__(message, details)
        self.message = message
        self.details = details
        print(f"Raised an exception: message: {self.message} details: {self.details}.")


#
# System Requirements: The SDK detects it can not perform tasks required of the system.
#


class SystemIntegrationError(SDKBaseException):
    def __init__(self, details=""):
        message = "Configuration error."
        super().__init__(message, details)


#
# Client API Caller
#


class ClientAPIThrottle(SDKBaseException):
    def __init__(self, details=""):
        message = "Request throttled. Too many requests."
        super().__init__(message, details)


#
# CONNECTING (MQTT)
#


# Can not connect to the service MQTT broker, likely a network issue.
class ConnectError(SDKBaseException):
    def __init__(self, details=""):
        message = "Connection error (MQTT)."
        super().__init__(message, details)


# Timed out connecting to the service MQTT broker, likely a network issue.
class ConnectTimeout(SDKBaseException):
    def __init__(self, details=""):
        message = "Connection timed out (MQTT)."
        super().__init__(message, details)


# Open SSL Setup
class SSLSetupError(SDKBaseException):
    def __init__(self, details=""):
        message = "SSL setup error."
        super().__init__(message, details)
#

# PAIRING
#


# Unknown pairing error, including 4xx rejecting the SDK pairing request.
class PairingError(SDKBaseException):
    def __init__(self, details=""):
        message = "Unknown pairing failure."
        super().__init__(message, details)


# The pairing service return 5xx.
class PairingServiceError(SDKBaseException):
    def __init__(self, details=""):
        message = "Pairing service is experiencing an internal error."
        super().__init__(message, details)


# The payload from the pairing service is invalid and can't be parsed.
class PairingServiceResponseError(SDKBaseException):
    def __init__(self, details=""):
        message = "Pairing service response was not valid."
        super().__init__(message, details)


class HostConfigurationError(SDKBaseException):
    def __init__(self, details=""):
        message = "HostConfiguration error."
        super().__init__(message, details)


# Common causes: No network connectivity, DNS resolution failure, Server is down or unreachable,
# Firewall blocking the connection, Invalid URL or hostname, Server forcibly closed the connection
# Network timeout during connection establishment.
class PairingServiceRequestConnectionError(SDKBaseException):
    def __init__(self, details=""):
        message = "Pairing unable to connect to the service."
        super().__init__(message, details)


# Common causes: Server is overloaded, Network congestion, Server processing taking too long.
class PairingServiceRequestTimeoutError(SDKBaseException):
    def __init__(self, details=""):
        message = "Pairing timed out connecting to the service."
        super().__init__(message, details)


#
# Certificates/Certs
#


class CertificatesError(SDKBaseException):
    def __init__(self, details=""):
        message = "Unknown certificates error."
        super().__init__(message, details)


class CertificatesInvalid(SDKBaseException):
    """
    Not authorized to connect to the service using the current certs. Client should deregister and re-pair
    to obtain new certs.
    """

    def __init__(self, details=""):
        message = "Certificates: Not authorized to connect to the service."
        super().__init__(message, details)


class CertificatesReadError(SDKBaseException):
    def __init__(self, details=""):
        message = "Certificates can not be read from the filesystem."
        super().__init__(message, details)


class CertificatesWriteError(SDKBaseException):
    def __init__(self, details=""):
        message = "Certificates can not be saved to the filesystem."
        super().__init__(message, details)


class CertificatesRotationError(SDKBaseException):
    """
    Raised when there is a problem rotating (changing / extending expiration of) credentials.
    """
    def __init__(self, details=""):
        message = "Certificates can not be rotated."
        super().__init__(message, details)

#
# Publishing
#


class MQTTPublishError(SDKBaseException):
    def __init__(self, details=""):
        message = "Publish failed."
        super().__init__(message, details)


class ReportStatusError(SDKBaseException):
    def __init__(self, details=""):
        message = "Publish: Report status failed."
        super().__init__(message, details)


class ReportSchemaError(SDKBaseException):
    def __init__(self, details=""):
        message = "Publish: Report schema failed."
        super().__init__(message, details)


#
# MESSAGE related errors
#


class InvalidConfigurationError(SDKBaseException):
    def __init__(self, details=""):
        message = "Invalid configuration message from the service was rejected."
        super().__init__(message, details)


class InvalidStatusMessageError(SDKBaseException):
    def __init__(self, details=""):
        message = "Invalid status message from the client was rejected."
        super().__init__(message, details)


# TODO: Add runtime checking for schema validation.
class InvalidSchemaError(SDKBaseException):
    def __init__(self, details=""):
        message = "Invalid schema was rejected."
        super().__init__(message, details)


#
# THUMBNAIL related errors
#
class InvalidThumbnailSubscription(SDKBaseException):
    def __init__(self, details=""):
        message = "Invalid Thumbnail subscription message from the service was rejected."
        super().__init__(message, details)


class ThumbnailProcessingError(SDKBaseException):
    def __init__(self, details=""):
        message = "Could not process Thumbnail subscription."
        super().__init__(message, details)

#
# Deprovision related errors
#
class InvalidDeprovisionRequest(SDKBaseException):
    def __init__(self, details=""):
        message = "Could not process deprovision message from host service."
        super().__init__(message, details)


class DeprovisionError(SDKBaseException):
    def __init__(self, details=""):
        message = "Unknown Deprovision error."
        super().__init__(message, details)
