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

from custom_exceptions import SystemIntegrationError
from host_settings import HostSettings


class Topics(object):
    """
    Protocol MQTT Topics as specified by the host_settings obtained during paring process.

    Params:
        device_id: Host-Service provided
        host_settings: Host-Service provided
    Raises:
        SystemIntegrationError: The service-specific topics were not properly defined.
    """

    def __init__(self, device_id: str, host_settings: HostSettings):
        print(f"Host Settings: {host_settings}")
        self.device_id = device_id
        try:
            # Subscribe: receiving schema-compliant configuration messages.
            self.update_configuration = host_settings.sub_update_topic

            # Subscribe: informs the client about the most current certs available.
            self.update_certs = host_settings.sub_update_certs_topic

            # Publish: sending scoped-schema to the service.
            self.report_schema = host_settings.pub_report_schema_topic

            # Publish: sending status to the service.
            self.report_status = host_settings.pub_report_status_topic

            print(f"Topics: Sub: {self.update_configuration}")
            print(f"Topics: Sub: {self.update_certs}")
            print(f"Topics: Pub: {self.report_schema}")
            print(f"Topics: Pub: {self.report_status}")
        except Exception as e:
            raise SystemIntegrationError(details="Could not load host MQTT Topics for service")

