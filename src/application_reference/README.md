#Application Reference Design

 This is a reference design implementation for a client application that communicates with a locally running CDD SDK.
 This assumes the Discovery Client SDK is able to connect to a running service. 
 
 The service must be able to:
- Claim the device.
- Show Status Updates
- Start/Stop the application streaming to an SRT listener endpoint.  

How it runs:
- Loops over connect to drive pairing, connection and return the SDK current state. 
- report_status(): Updates the application's status periodically.
- get_configuration():
    If properly configured, this application will start an FFMPEG web-cam stream
    via SRT the endpoint specified in the configuration payload.
