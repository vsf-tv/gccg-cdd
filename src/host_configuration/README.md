## host_id_template.json
The file host_id.protocol.template.json is a template
Use this file as a template to define a new file available on the device at

--host_configuration_path/<host_id>.json

<host_id>.json must contain entries / type described in the template. 
The SDK must fine this file when making an SDK API request to: connect(host_id)


## host_settings.protocol.template.json
The Cloud Host Service response to the GetPairingCode request must contain the host_settings JSON structure.
That host_settings response must contain entries / type described in this template.
This template is used to validate the response from the service conforms to this requirement.

