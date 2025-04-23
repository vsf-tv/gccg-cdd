# Client Device Discovery (CCD) Client SDK 
Discovery, monitoring and connection management of streaming video devices using an internet-secure, cloud 
and NAT friendly, scalable, pairing and communication protocol.

>Draft design documents related to this project are currently being discussed and revised in the VSF Bi-Weekly Forum.  
For access, please reach out to Brad Gilmer <brad@gilmer.tv> or Brian Rundle <brundle@amazon.com>.

## Introduction
CDD solves for discovering, managing and monitoring video devices from a scalable cloud service.
Customers tell us that the hardest part of cloud workflows is often getting their live signals connected 
in the first place. While there are many transport protocols available for securely streaming 
video (SRT, RIST, TR-07, etc), customers need to manually manage and monitor remote device access, correctly perform 
stream setup, including IP address, encryption keys and overcome networking obstacles like firewalls, 
network address translation and security groups.

We have started an activity group with the Video Services Forum (VSF) to develop a technical recommendation 
and an open-source SDK application providing device discovery, authentication and connection management 
that works with any transport protocol.

## Contents
- CDD Client SDK 
- Application reference design
- Instructions for installation, and running the Application Reference Design and CDD SDK. 


## Python External Dependencies
The following python external packages are required
- flask
- jsonschema
- paho.mqtt.client
- requests
- cryptography

## System Requirements
- Python 3.10 or newer
- RAM: SDK Consumes around 37MB
- File Read/Write


## Security
The SDK persists an identity and X509 credentials obtained during the pairing process in a path provided by the
host-system (the device on which the SDK is installed). While the protocol implements rotation to limit certificate
lifespan, securing credentials is the host-system's responsibility. The following are some best practices for
embedded systems:
- Verify Code Integrity: Allow only signed and trusted software run (bootloader, operating system, firmware).
- Hardware Root of Trust: Utilize hardware-based security mechanisms.
   (like Secure Elements or Trusted Platform Modules - TPMs) to establish an immutable root of trust for the boot process.
- Locking down remote access such as disabling SSH.
- Access Controls Tied to User/Process Context.  Linux SE for example.
- File system encryption such as LUKS (Linux Unified Key Setup) and fscrypt, Encrypting File System (EFS) and BitLocker.
- Regular Security Audits and Testing.


### Work in progress...

- Add thumbnails API
- Add deregister API
- Add standardized logging 
- Add telemetry
- Add unit and integration test
- Add Instance Schema rules validator


## Application Reference Design Prerequisite: FFMPEG
To be clear, this is not a SDK requirement, but used by the Application Reference Design (ARD) to simulate an
encoder device. Older versions of FFMPEG might not support SRT directly. Before proceeding, ensure it is
installed and test it directly using the following CLI command.


```bash
Start an SRT listener endpoint and get the ip:port:stream_id params.  One convenient option is
AWS Elemental Media Connect, but any SRT listener accessible by your system will do.
```

This configuration sets the device local web-cam as input (-i 0).  If a web-cam is not available on your system you
can modify the following CLI and application.py to use an alternate input source.  

On running the following, your web-cam should start, and video streamed via SRT to your SRT listener endpoint.
```bash
>ffmpeg -f avfoundation -framerate 30 -video_size 640x480 -i 0 -vcodec libx264 -f mpegts srt://{ip}:{port}/{stream_id}"
>cont-c  # to stop the stream
```

## Application Reference Design Prerequisite: API Caller Application
To be clear, this is not a SDK requirement, but used in the README instructions to make API calls on the VSF Host
Service Test Endpoint.  In practice, a host service will provide its own API access mechanism, GUI, etc.
Download or use your favorite API Caller application such as Postman, Hoppscotch, Insomnia, etc.
The application you chose must be able to make API calls formatted with headers for AWS Credentials
We will use this API Caller application to interact with the VSF Host Test Endpoint, claim the device, get status
and start, stop streaming.  


## Instructions

Currently, the VSF Test Endpoint is available at the following URL. This may change or include new endpoints.
> base_endpoint = https://jy7ae9g8oi.execute-api.us-east-1.amazonaws.com

### Create a cloud user/account.  

The VSF Test Endpoint is NOT an AWS service.  It is a simple cloud application test endpoint reference created 
and managed through the VSF strictly for CDD SDK testing and experiments.  It should never be used for production
and is available for VSF members to quickly download and verify the functionality of their CDD SDK client. 

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
                "arn:aws:execute-api:us-east-1:484202305601:*/*/*",
                "arn:aws:execute-api:us-east-1:484202305601:*/*/*/*",
                "arn:aws:execute-api:us-east-1:484202305601:*/*/*/*/*"
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

Step 2:
```bash
 Get Credentials to make API calls on the VSF Host Service Endpoint using your favorite API-Client application.  
 
 Go to: https://us-east-1.console.aws.amazon.com/iam
 > Click: Users
 Find: DiscoveryAPICaller user you created above
 > Click: Security and Credentials Tab
 Under the Access keys box click: Create Access Key
 > Select: Other
 > Select: Next
 > Select: Create Access Key
 Retrieve and securely store both your AccessKey & SecretKey.
 *** You must copy the secret key here, it is available only once! ***
```

Step 3
```bash
Test calling the VSF Test Endpoint using DiscoveryAPICaller credentials. 

You are going to call the "ListDevices" API.  Normally this will return all claimed/active devices.  Since we have not
yet claimed any devices, it will return success and an empty list.  

Create a GET request to: <base_endpoint>/dev/devices
Under Authorization Tab: 
Select: AWS Signature
Enter your AccessKey and SecretKey from above.
 
Expected Response: 
> A simple 200 response with an emtpy list 

While not too exciting it does demonstrate you are successfully calling the VSF 
test endpoint with a valid account!!
```





### Install the SDK and Application Reference Design
This instructions will show you how to download and install the SDK and the included application
reference design.

Step 0:
```bash
Install python 3.10 or greater on your system
```

Step 1:
```bash
Clone and cd into the CDD package
> git clone https://github.com/vsf-tv/gccg-cdd
> cd gccg-cdd
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

### Run the Application Reference Design
The following step will show you how to set up and run the Application Reference Design (ARD) and SDK.  
The SDK runs as a stand-alone process hosting a rest API.  The ARD simulates a video encoder host system making requests
on the SDK Rest API.  The SDK will connect to the host service defined by --host_id.  Both the ARD and SDK log to std 
out, so it's best to run the ARD and SDK in their own terminal to avoid confusion.

Step 0

```bash
Setup command line arguments.  The following syntax assumes BASH syntax, so adjust accordingly.  

The SDK will store credentials $CERTS_PATH/$ID when claimed.
> CERTS_PATH="<writeable and persistent folder, not /tmp>"

The ARD is a simple, one channel encoder capable of SRT outputs.  An example instance_schema is provided
that advertises the relevant settings.  
> INSTANCE_SCHEMA="$PWD/src/device_config/instance_schema.json"

For a production device, ID must be constant as the SDK places credentials in $CERTS_PATH/$ID.  
For testing, it is convenient have the option to supply a different ID to allow pairing multiple devices on
the same system without needing to de-provision them every time.  
> ID=my_device_123
```

Step 1:

```bash
Run the SDK Daemon.

The SDK will start, but will otherwise do nothing except quietly await API requests from the ARD.  
> python3 src/server_flask.py --certs_path $CERTS_PATH --schema_path $INSTANCE_SCHEMA --port 8603 --ip 127.0.0.1 --tmp_path /tmp --device_type ENCODER --internal_device_id  $ID
```

Step 2:
```bash
Start the Pairing Process.  

ARD acts as a simple FFMPEG encoder capable of running only a single channel with an SRT caller output using h264.  
The ARD will make a connect() request every few seconds.  The connect() response includes connection status, 
pairing if PAIRING is needed. 

The argument --host_id: vsf_test_host instructs the SDK to find the VSF Test Endpoint defined in 
src/host_configuration/vsf_test_host.json.   

Once started, the SDK looks for credentials in $CERTS_PATH/$ID.  
Since this 'device' has not yet been claimed, the SDK finds none.  As a result, the SDK starts the pairing process. 

Open a new terminal.  (STDOUT messages printed by both the ARD and SDK can thus be seen separately.)
cd <local cdd installation folder>
source venv/bin/activate
python3 ./src/application_reference/application.py --host_id vsf_test_host

Expected Output: 
> Device is not paired. Pairing Code: KY84IV  Expires in: 1799s
>       !copy the above Pairing Code: ^^^^^^
```

Step 3:
```bash
Claim the device.

Request VSF Host Test Endpoint to "claim" the device into your account using the DiscoveryAPICaller credentials.
Request:  <base_endpoint>/dev/authorize/{pairing-code}   e.g.   <base_endpoint>/dev/authorize/KY84IV
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

Now that the device is claimed, we can restart the SDK and/or the ARD and it will immediately reconnect. Try that now:
Choose either/both the SDK or the ARD terminal.  
> cont-c  to stop the process.  Up-Arrow/enter and restart it. 

```

### Manage the Device from the VSF Host Service Test Endpoint
Use the following VST Host Service API requests to get status, start, stop the device. 

Step 0
```bash
Get Status

This will request the latest status message posted by the ARD/SDK to the VSF Host Service.  
Request Path:  <base_endpoint>/dev/device/{device-id} 
Request Type: GET 
e.g.   <base_endpoint>/dev/device/001XI02IJ2FtSIirk01

Expected Response:
< A complete instance_schema-compliant status message json.>
```

Step 1



```bash
Start the encoder from the VSF Host Endpoint.  

This will update the latest configuration which is validated by the VSF Host Service and communicated to the device.
Edit: src/application_reference/example_config.json to point to your running SRT listener from the previous step.

Request Path:  <base_endpoint>/dev/device/{device-id} 
Request Type: PUT 
Request Body:
Copy the JSON from src/application_reference/example_config.json  

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
Edit: src/application_reference/example_config.json to point to your running SRT listener from the previous step.
Except this time change:
 "state": "ACTIVE" ->  "state": "IDLE",

Request Path:  <base_endpoint>/dev/device/{device-id} 
Request Type: PUT 
Request Body:
Copy the JSON from src/application_reference/example_config.json  

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

### De-Register or Un-claim the device
```bash
# This API is WIP and will be available soon. 
# For now, delete the credentials in $CERTS_PATH/$ID on the device.  You will be able to deprovision the 
# device in the service when this is implemented.  
```
