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
from service_api_models import HostSettings
from custom_logger import logger

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
        logger.info(f"Host Settings: {host_settings}")
        self.device_id = device_id
        try:
            # Subscribe: receiving schema-compliant configuration messages. (persistent topic)
            self.update_configuration = host_settings.sub_update_topic

            # Subscribe: informs the client about the most current certs available. (persistent topic)
            self.update_certs = host_settings.sub_update_certs_topic

            # Subscribe: informs the client about the current thumbnail subscription (persistent topic)
            self.update_thumbnail = host_settings.sub_update_thumbnail_subscription_topic

            # Publish: sending scoped-schema to the service.
            self.report_schema = host_settings.pub_report_schema_topic

            # Publish: sending status to the service.
            self.report_status = host_settings.pub_report_status_topic

            # Publish:  application requests deprovision, inform the service
            self.deprovision_inform_service = host_settings.pub_deprovision_topic

            # Subscribe: service requests deprovision, inform the client (persistent topic)
            self.deprovision_inform_client = host_settings.sub_deprovision_topic

            # Subscribe:  informs the client about the current log subscription (persistent topic)
            self.update_log = host_settings.sub_update_log_subscription_topic

            logger.info(f"Topics: Sub: {self.update_configuration}")
            logger.info(f"Topics: Sub: {self.update_certs}")
            logger.info(f"Topics: Sub: {self.update_thumbnail}")
            logger.info(f"Topics: Pub: {self.report_schema}")
            logger.info(f"Topics: Pub: {self.report_status}")
            logger.info(f"Topics: Pub: {self.deprovision_inform_service}")
            logger.info(f"Topics: Sub: {self.deprovision_inform_client}")
            logger.info(f"Topics: Pub: {self.update_log}")
        except Exception as e:
            raise SystemIntegrationError(details="Could not load host MQTT Topics for service")

