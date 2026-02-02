# Client Device Discovery (CDD) Client SDK: TR12
Discovery, monitoring and connection management of streaming video devices using an internet-secure, cloud 
and NAT friendly, scalable, pairing and communication protocol.

>Draft design documents related to this project are currently being discussed and revised in the VSF Bi-Weekly Forum.  
For access, please reach out to Brad Gilmer <brad@gilmer.tv> or Brian Rundle <brundle@amazon.com>.

## Introduction
CDD solves for discovering, managing and monitoring video devices from a scalable cloud service.
The hardest part of cloud workflows is often getting live signals connected to the cloud
in the first place. 

While there are many transport protocols available for securely streaming 
video (SRT, RIST, TR-07, etc), video production and distribution workflows that involve distributed
sources and destinations still need to be manually managed and monitored. Today, accessing devices
in distributed facilities requires cumbersome and not-scalable approaches like VPN tunneling, 
looking up devices by IP address, accees via usernames/passwords on a locally hosted console UIs.

CDD provides a mechanism to securely pair/discover devices into a (cloud) registry. Once connected,
a CDD enabled device can be managed and monitored anywhere in the world across the open internet. The
CDD protocol uses modern, cloud-first solutions for security, modeling, validation, and resource
lifecycle and applies those concepts for video streaming devices. A device can install the SDK, and
using the provided models, quickly integrate with the device's native control plane. A device user
can enable/disable the SDK, pair with a (cloud) host service of their choice and immediately have
persistent, portable access via that service. A CDD host service will support all CDD devices. 
The protocol solves for the widely differentiated settings (think codec, channels, etc) available from
different device types (encoders, decoders, cameras, playout devices) from different manufactures.
Devices can expose completely customized settings within the protocol's structure.   

CDD is a protocol that defines APIs (request/response) between clients (devices) and
host service. The SDK provided in this repository implements a CDD client. This repository 
also includes and Application Reference Design (ARD) to simulate a 1-channel encoder devices that integrates
the CDD SDK Client. Also provided is a cloud host service for testing. Using this readme, you should be able 
to install and test the ARD/SDK against with the VSF cloud endpoint in under 30 minutes. 
The VSF host service (deployed in AWS) has APIs for pair/describe/deprovision/configure/get thumbnails. 

Finally, this repository does not provide code for a CDD host service. In practice, modern cloud infrastructure
is highly differentiated between vendors and platforms. The ultimate goal for CDD is a concise TR12 specification
that results in an ecosystem of CDD production cloud services.    

## TR12 Protocol

1) Smithy Models (src/models) http/mqtt request/response models. 
2) The TR12 Protocol document available: http:<vsf> defines additional client/service requirements.

## Architecture
The SDK client provided in this repo is a python process hosting a Rest API on localhost. The device application uses the 
generated models (provided for most languages) for creating API requests, handling API responses to the SDK
process.  The SDK handles connecting and communicating the host service via http and mqtt. 
equires https/Port 443 outbound access.
No other firewall, port forwarding is required. Possibly a containerized version will be available soon. 


## Contents
- CDD Client SDK 
- Application reference design
- Instructions for installation, and running the Application Reference Design and CDD SDK. 

## Python External Dependencies
The CDD SDK here implemented in python. The following python external packages are required.
- flask
- jsonschema
- paho.mqtt.client
- requests
- cryptography 
- attrs 
- cattrs 
- pytest 
- referencing
- urllib3

## Build Dependency
- build dependency: smithy/open-api


## System Requirements
- Python 3.12 or newer plus dependencies listed above
- RAM: SDK Consumes around 60MB
- File system: Persistent (across power cycles) Read/Write.  Minimal storage for credentials, optional logs.

## Security
The SDK persists an identity and X509 credentials (on disk) obtained during the pairing process in a path provided by the
host service. While the protocol implements credential rotation to limit certificate lifespan, 
securing credentials is the host-system's responsibility. 

The following are some best security practices for embedded systems:
- Verify Code Integrity: Allow only signed and trusted software run (bootloader, operating system, firmware).
- Hardware Root of Trust: Utilize hardware-based security mechanisms.
   (like Secure Elements or Trusted Platform Modules - TPMs) to establish an immutable root of trust for the boot process.
- Locking down remote access such as disabling SSH.
- Access Controls Tied to User/Process Context.  Linux SE for example.
- File system encryption such as LUKS (Linux Unified Key Setup) and fscrypt, Encrypting File System (EFS) and BitLocker.
- Regular Security Audits and Testing.


## Application Reference Design (ARD) Pre-Flight: FFMPEG
Older versions of FFMPEG might not support SRT directly. Before proceeding, ensure ffmpeg is
installed and test it directly using the following CLI command that connects a standard internal web-cam
 streams via SRT to your SRT listener endpoint.  (You need to start the lister endpoint yourself)
 
>ffmpeg -f avfoundation -framerate 30 -video_size 640x480 -i 0 -vcodec libx264 -f mpegts srt://{ip}:{port}/{stream_id}"
>cont-c  # to stop the stream


## API Caller Application
To test the SDK againt the VSF Test Host Service, we will need to make authenticated API calls on the VSF Host
Service Endpoint. In production, a CDD host service will provide its own API access mechanism, GUI, etc.

Download or use your favorite API Caller application such as Postman, Hoppscotch, Insomnia, etc.
The application you chose must be able to make API calls formatted with headers using AWS Credentials.
We will use this API Caller application to interact with the VSF Host Test Endpoint, claim the device, get status
and start, stop streaming.  


## Instructions

Currently, the VSF Test Endpoint is available at the following URL. This may change or include new endpoints.
This endpoint is not a production service and may be removed/replaced at any time. 
> base_endpoint = https://v5v7zhbk3k.execute-api.us-east-1.amazonaws.com/dev

## The VSF Test Host Service Endpoint

** The VSF Test Endpoint is simply a testing tool privately vended by the VSF and is NOT an AWS service. **
It should never be used for production and is available for VSF members to quickly download and verify the
functionality of their CDD SDK client.

## Create AWS Credentials to access the endpoint. 

Step 0:
```bash
Login into or create an AWS account.
```

Step 1:
```bash
 Create an IAM user

 This creates an IAM user with no permissions within the context of your AWS account except to execute-api calls
 on APIs hosted by the VSF test endpoint.  Devices claimed by the user will be accessible by all users
 under same AWS *account*.  
 
 The endpoint is deployed using AWS cloud infrastructure but is not an AWS service.  
 Go to: https://us-east-1.console.aws.amazon.com/iam
> Select: Users
> Select: Create User (button upper right).
> Enter: DiscoveryAPICaller
> Select: "Attach Policies Directly"
> Click: Create Policy      (This opens up a new TAB/Window)
 In the Policy Editor:
   Select JSON
   Replace the policy with the following:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "execute-api:Invoke",
            "Resource": [
                "arn:aws:execute-api:*:484202305601:*/*/*",
                "arn:aws:execute-api:*:484202305601:*/*/*/*",
                "arn:aws:execute-api:*:484202305601:*/*/*/*/*"
            ]
        }
    ]
}

> Click: Next
Name the Policy: "DiscoveryAPICallerPolicy"
> Click:  CreatePolicy

Go back to the Create User browser tab attach the policy you just created to the user.
Under "Permissions Policy" enter the new policy name: DiscoveryAPICallerPolicy 
DiscoveryAPICallerPolicy should appear
>    Select: the checkbox for this policy when it shows up
>    Click: Next
>    Click: Create User
    Verify
    The IAM user: DiscoveryAPICaller should have the policy you set under the permissions tab.  
```

Step 2 
Get Temporary Credentials (configurable 1-12 hours) to call the VSF host service API
```bash
 Log in to the AWS console as user: DiscoveryAPICaller

 https://YOUR_ACCOUNT_ID.signin.aws.amazon.com/console
 Click Switch Role.
 Enter your Account ID, IAM user name: "DiscoveryAPICaller" and your password.

Open the AWS Cloud Shell console.
Verify your identity as: DiscoveryAPICaller
> aws sts get-caller-identity

Export Temporary Credentials:
> aws configure export-credentials --format env
 
 Retrieve: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN for use in calling the APIs below. 

  
```

Step 3
```bash
Test calling the VSF Test Endpoint using DiscoveryAPICaller credentials. 

You are going to call the "ListDevices" API.  This returns all ACTIVE device in your cloud service registry.
Since we have not yet claimed any devices into your repository, it will return success (200) and an empty list.  

Create a Rest GET request to: "<base_endpoint>/devices"

Authorization Type: Select: "AWS Signature" 
Enter: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
Region: us-east-1
 
Expected Response: 
> A simple 200 response with an emtpy list 

While not too exciting, it does demonstrate you are successfully calling the VSF test endpoint with a valid AWS user!
```




### Install the SDK and Application Reference Design
OK lets go back and install the SDK and get things working on the client/device side of things. 

Step 0:
```bash
Requried:
1) Install python 3.12 or greater on your system
> python --version 
```


Step 1:
```bash
Clone and cd into the CDD package
> git clone https://github.com/vsf-tv/gccg-cdd
> cd gccg-cdd ( the CDK Root dir )
> ls
You should see a src/ dir and requirements.txt   
```

Step 2:
```bash
nstall a python virtual environment
> python3 -m venv venv
```

Step 3:
```bash
Activate your python virtual environment
> source venv/bin/activate
```

Step 4:

```bash
Install python external dependencies (listed in requirements.txt) into your python virtual env.
> pip3 install -r requirements.txt
````

(Optional: Not needed for the ARD demo)
```bash
 Install Smithy
 This is only needed if your intention is integrate the SDK into a c++ or other non-python application. 

   a) MAC > brew install smithy
   b) LINUX/PC/Other: See: https://github.com/smithy-lang/smithy/  
     
Build the open-api models from the TR12 Smithy definitions.  This creates a python 'SDK'
 - Models and Validators for the CDD SDK local APis
 - Models and Validators for the TR12 Protocol 
 
The Createed in: 
src/generatedSDK<language>
  
  This uses smithy-build.json and smithy-build-internal.json
   > cd <sdk root>
   > smithy build 
   > ./generate-sdk.sh <your application langauge>
   
```

### Start the CDD SDK and use the Application Reference Design (ARD)
The following step run the Application Reference Design (ARD) and CDD SDK.  
The SDK runs as a stand-alone process hosting a rest API.  The ARD simulates a video encoder host system making requests
on the SDK Rest API.  The SDK will connect to the host service defined by --host_id.  Both the ARD and SDK log to std 
out, so it's best to run the ARD and SDK in their own terminal to avoid confusion.

Step 0

```bash
Setup command line arguments.  The following syntax assumes BASH syntax, so adjust accordingly.  

The SDK will store credentials $CERTS_PATH/$ID when claimed.
> export CERTS_PATH="<writeable and persistent folder, not /tmp>"
> export ID=my_device_123   
```

Step 1:

```bash
Start the SDK Daemon.

The SDK will start, but will otherwise do nothing except quietly await API requests from the ARD.  
In Terminal Window #1
1> python3 src/server_flask.py --certs_path $CERTS_PATH --registration_file_path <cdd sdk path>/src/payloads/1_channel_encoder/registration.json  --port 8603 --ip 127.0.0.1 --tmp_path /tmp --device_type [SOURCE | DESTINATION | BOTH] --internal_device_id  $ID --log_path /tmp/ 
``` 

Step 2:
```bash

Start the Application Reference Design.
In Terminal Window #2
2> python3 ./src/application_reference/application.py --host_id vsf_test_host

What happens: 

  The ARD has never being claimed into a host service...not yet.  
  The ARD will make a connect() request on the SDK
  The SDK will connect to the VSF cloud test service definded in the file src/host_configuration/vsf_test_host.json

  The SDK looks for credentials in $CERTS_PATH/$ID.  
  The SDK finds none.  
  The SDK starts the pairing process and should give you the Pairing Code


Expected Output: 
> Device is not paired. Pairing Code: KY84IV  Expires in: 1799s
>       !copy the above Pairing Code: ^^^^^^
```

```bash
Claim the device into the VSF cloud test registry 

From here well make API calls to the CDD VSF Cloud Test endpoint.  This requres an AWS account you used
in the setup.  

Request VSF Host Test Endpoint to "claim" the device into your account using the DiscoveryAPICaller credentials.
Request: <base_endpoint>/authorize/{pairing-code}   e.g.  <base_endpoint>/authorize/KY84IV
Request Type: PUT 
Request Authorization:  AWS Signature (or similar depending on your API Caller application)

Expected response:
> {"status": "success", "message": "Success!"}
```

Step 4
```bash
Monitor output of the ARD and the SDK.  

In less than a second, the device is claimed, has connected to the service and the ARD displays the 
service-assigned "device_id".  The ARD output will look something like: 
> run_loop Success: True State: CONNECTED  error: None DeviceID: 001XI02IJ2FtSIirk01  message: Connected

The SDK stdout output is somewhat more verbose. 

Now that the device is claimed, we could restart the SDK and/or the ARD and it will immediately reconnect. Try that now:
Choose either/both the SDK or the ARD terminal.  
> cont-c  to stop the process.  Up-Arrow/enter and restart it. 

```

### Manage the Device from the VSF Host Service Test Endpoint
Use the following VST Host Service API requests to get status, start, stop the device. 

Step 0
```bash
Get Status (DescribeDevice)

This will request the latest status message posted by the ARD/SDK to the VSF Host Service.  
Request Path: <base_endpoint>/device/{device-id}
Request Path: <base_endpoint>/device/{device-id}?include_schema=true|false
Request Type: GET 
e.g.  <base_endpoint>/device/001XI02IJ2FtSIirk01

Expected Response is someething like:
{
  "device_id": "string - Device identifier",
  "message": "string - Response message",
  "errors": ["array of error strings"],
  "status": {"dict - Current device status data"},
  "configuration": {"dict - Device configuration settings"},
  "registration": {"dict - Device registration file: information provided"},
  "online_details": "string - Connection status details (default: 'offline: -h-m-s')",
  "online": "boolean - Device online status",
  "cert_expiration": "string - Certificate expiration info",
  "device_metadata": {
    "online": "boolean - Online status",
    "online_details": "string - Detailed connection info",
    "cert_expiration": "string - Certificate expiration",
    "source_ip": "string - Device source IP address"
  }
}


Get All Devices (ListDevices)
This will return all devices currently regitered.
Request Path: <base_endpoint>/devices/
Request Type: GET
e.g.  <base_endpoint>/devices

Expected Response:
[
    {
        "device_id": "001XI02IJ2FtSIirk01",
        "message": "",
        "errors": [],
        "online_details": "online: 0d 0h 11m",
        "online": true
    }
    ,
    ...
]

```

Step 1



```bash
Start the encoder from the VSF Host Endpoint.  

This will update the latest configuration which is validated by the VSF Host Service and communicated to the device.
Edit: src/payloads/1_channel_encoder/configuration.json to point to your running SRT listener from the previous step.
You will need to provide values for your specific:
1. IP, Port using srtCaller.  (At this time, the ARD only streams with srtCaller)
      
Request Path: <base_endpoint>/device/{device-id} 
Request Type: PUT 
Request Body:
Copy the JSON from src/payloads/1_channel_encoder/configuration.json

Note: If using POSTMAN:  In the 'Body' Tab, Select 'Raw' Type.  Paste the configuration.json


Expected Host Service Response:
{
    "device_id": "..................",
    "message": "Device updated",
    "error": ""
}

Any error in matching the configuration to the instance schema will result in an error.  The API should return details
of the validation problem. 

Expected SDK and ARD behavior:
<The ARD should start streaming to your SRT listener endpoint>
```

Step 2

```bash
Stop the encoder from the VSF Host Endpoint.  

This will update the latest configuration which is validated by the VSF Host Service and communicated to the device.
Edit: src/payloads/1_channel_encoder/configuration.json to point to your running SRT listener from the previous step.
Except the this time change the Channel param: 
 "state": "ACTIVE" ->  "state": "IDLE",

Request Path: <base_endpoint>/device/{device-id} 
Request Type: PUT 
Request Body:
Copy the JSON from src/payloads/1_channel_encoder/configuration.json

Expected Host Service Response:
{
    "device_id": "..................",
    "message": "Device updated",
    "error": ""
}

Any error in matching the configuration to the instance schema will result in an error.  The API should return details
of the validation problem. 

Expected SDK and ARD behavior
<The ARD should stop streaming.>
```

### Test Cert Rotation
The SDK supports credential (cert) rotation.  In practice, a Host Service will rotate and expire certs automatically.
For testing purposes, a rotation API is provided that allows manual cert rotation.  Connected devices will process the
rotation message and reconnected with updated certs.  Offline devices will not pick up any rotated credentials and risk
expiration.  Rotation is an essential practice that reduces the threat posed by stolen credentials.  The rotation
interval is determined by the Host Service and likely set by the customer within a min/max range.

Note: Cert rotation is complete on the SDK, but auto-rotation and expiration is currently WIP in the VSF Host Service
Test Endpoint.  This manual API allows testing while those features are added.


```bash
Rotate Credentials and Describe Device to check the new expiration.

Request Path:<base_endpoint>/credentials/{device-id}
Request Type: PUT

Expected Host Service Response:
{
    "device_id": ...,
    "message": "Credentials successfully rotated.",
    "error": ""
}

Get Status to see the updated credential expiration
Request Path: <base_endpoint>/device/{device-id}
Request Type: GET
e.g.  <base_endpoint>/device/001XI02IJ2FtSIirk01

Expected Host Service Response:
{
    "device_id": ...,
    ...

    "cert_expiration": "23d 20h 63m",
}

```

### Test Thumbnails
```bash
Application Reference Design (ARD) emits a series of thumbnails to /tmp/image_sdi.jpg and /tmp/image_hdmi.jpg.
These represent images from both the SDI-1 and HDMI-1 sources. Availability and location are defined in the
schema and status message (see instance_schema.json and example_status.json). The SDK delivers images to the
Host Service in response to a "subscription" request. The application need only emit images to the local_path.
The SDK handles the rest including managing the rate, expiration, and transmission.

This example allows you to make a Get Thumbnail API call to the Host Service Test Endpoint which passes a new
thumbnail subscription to the device.

Protocol Restrictions:
- Each service advertises the max supported file size in the host_configration file ("thumbnail_max_size_KB": int)
- Images older than 10s are deemed stale and will not be transmitted.  This ensures only actively produced images
  are sent.  Additionally means that devices need not actively delete old images to prevent them from being transmitted.

The following is an example Host Service Test Endpoint API.  You can repeatedly call this API to get a fresh image.
The first response may be empty as the new subscription is being processed.

The <thumbnail_id> is provided in the registration_file returned via the DescribeDevice API
This file is provided by the application reference design on SDK startup.  See: CDD Message Protocol

Request Path: <base_endpoint>/device/{device-id}?source=<thumbnail_id>
Request Type: GET
e.g.  <base_endpoint>/device/001XI02IJ2FtSIirk01?source=SDI-1
e.g.  <base_endpoint>/device/001XI02IJ2FtSIirk01?source=HDMI-1

Expected Host Service Response:
{
    "message": "Thumbnail request expires in: 120",
    "image": {
        "base64_image": A base 64 encoded image of type <image_type>,
        "timestamp": "2025-05-14 16:28:02 UTC",
        "image_type": "jpg",
        "max_size_KB": 250,   <- Max size support by the Host Service
        "image_size_KB": 139
    }
}

To view the image you must base64 decode base64_image and open in an appropriate jpg or png viewing application.  

```



### De-Register or Un-claim the device
```bash
# This initiates an un-pairing process on the client.  A connected client will be disconnected.
# A client that is in a DISCONNECTED state when deprovisioned, will be able to connect at a later time where it will
# immediately be deprovision and be disconnected. 

# Once deprovisoined, any subsequent call to connect will start the pairing process.  

Request Path: <base_endpoint>/deprovision/{device-id}
Request Type: PUT
e.g.  <base_endpoint>/deprovision/001XI02IJ2FtSIirk01

Expected Host Service Response:
{
    "device_id": "001XI02IJ2FtSIirk01",
    "message": "Deprovisioned device: 001XI02IJ2FtSIirk01.",
    "errors": []
}

# Check the device is no longer a registered device (see DescribeDevice/ListDevices above).
```

### Developer Instructions

The CDD Protocol schemas are maintained in a manageable, hierarchal form. These will restricted to update pull-requests
generally since they codify the CDD message payload.  That said, when updating, make changes to the following
hierarchal and easy to read/edit schemas in:
```bash
<cdd>/src/schemas/  
```
After any changes, run
```bash
<cdd>/src/schemas/compile_schemas.py
```

The resulting schemas used by the SDK are collapsed and written here for easy loading by the SDK.
```bash
<cdd>/src/compiled_schemas/
```

The developer can validate changes by runninng
```bash
<cdd>/src/schemas/validate_schemas.py
<cdd>/src/schemas/validate_compiled_schemas.py

```
