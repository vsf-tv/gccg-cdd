"""
TR-12 Client Device Discovery (CDD) SDK

This package provides the TR-12 CDD SDK for discovering, monitoring and 
connection management of streaming video devices.
"""

# Main SDK class
from .discovery_sdk import CddSdk

# Core utilities
from .credentialstore import CredentialStore
from .states import States
from .custom_exceptions import (
    ConnectError,
    PairingError,
    DeprovisionError,
    InvalidConfigurationError,
    ReportStatusError
)

# Model validators
from .model_validator import (
    validate_configuration,
    validate_registration,
    validate_status
)

__version__ = "1.0.0"
__all__ = [
    "CddSdk",
    "CredentialStore", 
    "States",
    "ConnectError",
    "PairingError",
    "DeprovisionError",
    "InvalidConfigurationError",
    "ReportStatusError",
    "validate_configuration",
    "validate_registration", 
    "validate_status"
]