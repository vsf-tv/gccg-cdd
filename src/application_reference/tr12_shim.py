"""
TR-12 Model Shim — walks auto-generated SMITHY registration/configuration
structures and dispatches to device-specific callbacks so integrators only
need to fill in get/set logic for their native API.

Model Structure Summary:

Configuration (apply):
  DeviceConfiguration
    ├── simple_settings: List[IdAndValue]  # device-level settings
    │   └── IdAndValue: {key: str, value: str}
    └── channels: List[ChannelConfiguration]
        ├── id: str
        ├── state: ChannelState
        ├── settings: SettingsChoice (oneOf SimpleSettings | Profile)
        │   ├── SimpleSettings.simple_settings: List[IdAndValue]
        │   └── Profile.profile: SettingProfile{id: str}
        └── connection: Connection
            └── transport_protocol: TransportProtocol (oneOf SrtCaller|...)

Registration (get):
  DeviceRegistration
    ├── simple_settings: List[Setting]  # defines available device settings
    │   └── Setting: {id: str, name: str, info: str, enums?, ranges?}
    └── channels: List[Channel]
        ├── id: str
        ├── simple_settings: List[Setting]  # defines available channel settings
        ├── profiles: List[ProfileDefinition]  # available profiles
        └── connection_protocols: List[SupportedProtocol]
"""

from __future__ import annotations

import logging
from typing import Optional

from cdd_sdk_client.models.channel import Channel
from cdd_sdk_client.models.channel_configuration import ChannelConfiguration
from cdd_sdk_client.models.channel_state import ChannelState
from cdd_sdk_client.models.device_configuration import DeviceConfiguration
from cdd_sdk_client.models.device_registration import DeviceRegistration
from cdd_sdk_client.models.id_and_value import IdAndValue
from cdd_sdk_client.models.profile import Profile
from cdd_sdk_client.models.setting_profile import SettingProfile
from cdd_sdk_client.models.settings_choice import SettingsChoice
from cdd_sdk_client.models.simple_settings import SimpleSettings
from cdd_sdk_client.models.device_status import DeviceStatus

from tr12_callbacks import Callbacks

logger = logging.getLogger(__name__)


class Tr12Shim:
    """Walks TR-12 SMITHY models and bridges them to device callbacks.

    Instantiates a Callbacks object internally which provides:

    *Apply (set) side* - called when applying a desired configuration
        update_device_key_value(key, value)
        update_channel_settings(channel_id, key, value)
        update_channel_profile(channel_id, profile_id)
        update_channel_connection(channel_id, Connection)
        update_channel_state(channel_id, ChannelState)

    *Get (read-back) side* - called when building actual configuration
        get_device_updated_value(key) -> Optional[str]
        get_channel_updated_value(channel_id, key) -> Optional[str]
        get_channel_profile_value(channel_id) -> Optional[str]
        get_channel_connection(channel_id) -> Optional[Connection]
        get_channel_state(channel_id) -> ChannelState
    """

    def __init__(self, callbacks: Callbacks):
        self.callbacks = callbacks
    # ------------------------------------------------------------------
    # Apply desired configuration
    # ------------------------------------------------------------------

    def apply_desired_configuration(
        self, desired: DeviceConfiguration
    ) -> bool:
        """Walk *desired* DeviceConfiguration, push every value to the device
        via the callbacks, then return True on success.
        
        DeviceConfiguration structure:
          - simple_settings: List[IdAndValue] where IdAndValue has {key, value}
          - channels: List[ChannelConfiguration]
        """
        try:
            if desired is None:
                return False

            # Device-level simple settings (List[IdAndValue])
            if desired.simple_settings:
                for kv in desired.simple_settings:
                    self.callbacks.update_device_key_value(kv.key, kv.value)

            # Per-channel configuration
            if desired.channels:
                for ch_cfg in desired.channels:
                    self._apply_channel(ch_cfg)

            return True
        except Exception as e:
            logger.error(f"Error applying configuration: {e}")

        return False

    def _apply_channel(self, ch_cfg: ChannelConfiguration) -> None:
        """Apply a single ChannelConfiguration.
        
        ChannelConfiguration structure:
          - id: str
          - state: ChannelState
          - settings: Optional[SettingsChoice] (oneOf SimpleSettings | Profile)
          - connection: Optional[Connection]
        """
        ch_id = ch_cfg.id

        # Settings is a SettingsChoice which is a oneOf wrapper
        # Its actual_instance can be SimpleSettings or Profile
        if ch_cfg.settings is not None:
            instance = ch_cfg.settings.actual_instance
            if instance is not None:
                if isinstance(instance, SimpleSettings):
                    for kv in instance.simple_settings:
                        self.callbacks.update_channel_settings(ch_id, kv.key, kv.value)
                elif isinstance(instance, Profile):
                    profile_id = instance.profile.id
                    self.callbacks.update_channel_profile(ch_id, profile_id)

        # Connection
        if ch_cfg.connection is not None:
            self.callbacks.update_channel_connection(ch_id, ch_cfg.connection)

        # State (apply last so settings/connection are in place first)
        if ch_cfg.state is not None:
            self.callbacks.update_channel_state(ch_id, ch_cfg.state)

    # ------------------------------------------------------------------
    # Get actual configuration
    # ------------------------------------------------------------------

    def get_actual_configuration(
        self, registration: DeviceRegistration
    ) -> Optional[DeviceConfiguration]:
        """Walk the *registration* to discover which settings are exposed,
        read back current values via the callbacks, and return a
        populated DeviceConfiguration.
        
        DeviceRegistration structure:
          - simple_settings: List[Setting] where Setting has {id, name, info, enums?, ranges?}
          - channels: List[Channel]
        """
        try:
            device_settings: list[IdAndValue] = []
            if registration.simple_settings:
                for setting in registration.simple_settings:
                    value = self.callbacks.get_device_updated_value(setting.id)
                    if value is not None:
                        device_settings.append(IdAndValue(key=setting.id, value=value))

            channel_configs: list[ChannelConfiguration] = []
            if registration.channels:
                for reg_ch in registration.channels:
                    channel_configs.append(self._build_channel_config(reg_ch))

            return DeviceConfiguration(
                channels=channel_configs,
                simple_settings=device_settings if device_settings else None,
            )
        except Exception as e:
            logger.error(f"Error getting actual configuration: {e}")

        return None

    def _build_channel_config(self, reg_ch: Channel) -> ChannelConfiguration:
        """Build a ChannelConfiguration from a Channel registration."""
        ch_id = reg_ch.id

        settings_choice: Optional[SettingsChoice] = None
        
        # Check if device uses profiles for this channel
        if reg_ch.profiles:
            profile_id = self.callbacks.get_channel_profile_value(ch_id)
            if profile_id is not None:
                settings_choice = SettingsChoice(
                    actual_instance=Profile(profile=SettingProfile(id=profile_id))
                )
        
        # If no profile, use simple settings
        if settings_choice is None and reg_ch.simple_settings:
            kv_list: list[IdAndValue] = []
            for setting in reg_ch.simple_settings:
                # BUG WORKAROUND: Host service currently sends Setting.name as the key
                # instead of Setting.id. Using name until host service is fixed.
                # Correct key should be: setting.id
                value = self.callbacks.get_channel_updated_value(ch_id, setting.name)
                if value is not None:
                    kv_list.append(IdAndValue(key=setting.name, value=value))
            if kv_list:
                settings_choice = SettingsChoice(
                    actual_instance=SimpleSettings(simple_settings=kv_list)
                )

        connection = self.callbacks.get_channel_connection(ch_id)
        state = self.callbacks.get_channel_state(ch_id)

        return ChannelConfiguration(
            id=ch_id,
            state=state,
            settings=settings_choice,
            connection=connection,
        )

    def get_device_status(self) -> DeviceStatus:
        """Build device status dict using callbacks.
        
        Returns a DeviceStatus structure:
          - status: List[{name, value, info}]  # device-level status
          - channels: List[{id, state, status: List[{name, value, info}]}]
        """
        try:
            # Device-level status from callbacks
            device_status = self.callbacks.get_device_status()

            # Channel status - get from encoder for each channel
            # For now, hardcode CH01 as that's what the ARD uses
            channel_id = "CH01"
            channel_state = self.callbacks.get_channel_state(channel_id)
            channel_status = self.callbacks.get_channel_status(channel_id)

            status_payload = {
                "status": device_status,
                "channels": [
                    {
                        "id": channel_id,
                        "state": channel_state,
                        "status": channel_status
                    }
                ]
            }
            return DeviceStatus.from_dict(status_payload)

        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return None
