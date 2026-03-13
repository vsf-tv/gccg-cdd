$version: "2"

namespace com.example.cdd

use aws.protocols#restJson1
use com.example.cdd.configuration#DeviceConfiguration
use com.example.cdd.registration#DeviceRegistration
use com.example.cdd.status#DeviceStatus

@restJson1
service CddService {
    version: "1.0"
    operations: [
        Connect,
        Disconnect,
        GetConnectionStatus,
        Deprovision,
        GetConfiguration,
        ReportStatus,
        ReportActualConfiguration
    ]
}

// PUT /connect - JSON body with registration and hostId
@http(method: "PUT", uri: "/connect")
operation Connect {
    input: ConnectInput
    output: ConnectOutput
}

// PUT /disconnect - no input
@http(method: "PUT", uri: "/disconnect")
operation Disconnect {
    output: BaseResponse
}

// GET /get_state - no input
@http(method: "GET", uri: "/get_state")
operation GetConnectionStatus {
    output: BaseResponse
}

// PUT /deprovision - query params: host_id, force
@http(method: "PUT", uri: "/deprovision")
operation Deprovision {
    input: DeprovisionInput
    output: BaseResponse
}

// GET /get_configuration - no input
@readonly
@http(method: "GET", uri: "/get_configuration")
operation GetConfiguration {
    output: GetConfigurationOutput
}

// PUT /report_status - JSON body with status
@http(method: "PUT", uri: "/report_status")
operation ReportStatus {
    input: ReportStatusInput
    output: BaseResponse
}

// PUT /report_actual_configuration - JSON body with configuration
@http(method: "PUT", uri: "/report_actual_configuration")
operation ReportActualConfiguration {
    input: ReportActualConfigurationInput
    output: BaseResponse
}

// Input structures
structure ConnectInput {
    @required
    registration: DeviceRegistration,
    @required
    hostId: String
}

structure DeprovisionInput {
    @required
    @httpQuery("host_id")
    hostId: String,
    @httpQuery("force")
    force: Boolean
}

structure ReportStatusInput {
    @required
    status: DeviceStatus
}

structure ReportActualConfigurationInput {
    @required
    configuration: DeviceConfiguration
}

// Output structures
structure BaseResponse {
    @required
    success: Boolean,
    @required
    state: String,
    @required
    message: String,
    error: ErrorDetails
}

structure ConnectOutput {
    @required
    success: Boolean,
    @required
    state: String,
    @required
    message: String,
    error: ErrorDetails,
    deviceId: String,
    region: String,
    pairingCode: String,
    expires: Integer
}

structure GetConfigurationOutput {
    @required
    success: Boolean,
    @required
    state: String,
    @required
    message: String,
    error: ErrorDetails,
    configuration: ConfigurationData
}

structure ErrorDetails {
    @required
    type: String,
    @required
    message: String,
    @required
    details: String
}

structure ConfigurationData {
    updateId: String,
    payload: DeviceConfiguration
}