# device_config 


### Template_Schema 
Defines the Discovery Status, Configuration and SDK Telemetry Payloads. 

### Instance_Schema
Each device can scope down the Protocol Schema to support only those parameters supported by the device.
A device may create an instance schema that conforms to inheritance rules define here:  
https://docs.google.com/document/d/1_rhiDNNU2hGQ2Rih3MYGSRIy9x17cy5wZywx00Z8A1M/edit?usp=sharing

### Enforcement
- The Application must supply an instance_schema when starting the SDK.
- The Application must verify the instance_schema obeys inheritance rules. (Tool is WIP, but will be added to the SDK)
- The SDK will validate all payloads on report_status against the scoped_schema, and on getting an updated configuration
from the service.
- The Host Service shall validate all payloads received by the client and service API caller.