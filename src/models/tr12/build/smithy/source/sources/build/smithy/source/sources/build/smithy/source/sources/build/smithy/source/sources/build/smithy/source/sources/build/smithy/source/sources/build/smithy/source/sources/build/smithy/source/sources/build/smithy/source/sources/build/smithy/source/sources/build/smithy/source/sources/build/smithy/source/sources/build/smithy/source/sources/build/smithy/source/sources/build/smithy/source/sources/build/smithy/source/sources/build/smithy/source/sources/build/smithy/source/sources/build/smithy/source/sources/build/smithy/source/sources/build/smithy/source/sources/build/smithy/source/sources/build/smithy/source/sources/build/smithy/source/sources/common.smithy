$version: "2"

namespace com.example.cdd.common

structure ProtocolVersion {
    @default("1.0.0")
    version: String
}

enum ChannelState {
    ACTIVE
    IDLE
}

enum ChannelType {
    SOURCE
    DESTINATION
}

enum AuthStatus {
    STANDBY
    CLAIMED
}

enum SupportedProtocol {
    SRT_LISTENER
    SRT_CALLER
    ZIXI_LISTENER
    ZIXI_CALLER
    RIST_CALLER
    RIST_LISTENER
}

structure IdAndValue {
    @required
    key: String
    @required
    value: String
}

//TODO: make this a map
list IdAndValueList {
    member: IdAndValue
}

list StringList {
    member: String
}

structure HostSettings {
    @required
    // TODO: should this be an enum?
    // TODO: Do we want to expose iot or keep that as an implementation detail?
    iotProtocolName: String
    @required
    pairingTimeoutSeconds: Integer
    @required
    minIntervalPubSeconds: Integer
    @required
    mqttKeepaliveSeconds: Integer
    @required
    subUpdateTopic: String
    @required
    subUpdateThumbnailSubscriptionTopic: String
    @required
    pubReportSchemaTopic: String
    @required
    pubReportRegistrationTopic: String
    @required
    pubReportStatusTopic: String
    @required
    pubReportActualConfigurationTopic: String
    @required
    subUpdateCertsTopic: String
    @required
    pubDeprovisionTopic: String
    @required
    subDeprovisionTopic: String
    @required
    subUpdateLogSubscriptionTopic: String
}

structure PairRequest {
    @required
    deviceType: String
    @required
    hostId: String
    @required
    csr: String
    @required
    version: String
}

enum PairFailureReason {
    HOST_ID_MISMATCH
    VERSION_NOT_SUPPORTED
    DEVICE_TYPE_NOT_SUPPORTED
}

union PairResult {
    success: PairSuccessData
    failure: PairFailureData
}

structure PairSuccessData {
    @required
    deviceId: String
    @required
    pairingCode: String
    @required
    accessCode: String
    @required
    pairingTimeoutSeconds: Integer
}

structure PairFailureData {
    @required
    reason: PairFailureReason
}

structure PairResponse {
    @required
    result: PairResult
}

structure AuthRequest {
    @required
    deviceId: String
    @required
    pairingCode: String
    @required
    accessCode: String
}

structure AuthResponse {
    @required
    status: AuthStatus
    caCert: String
    deviceCert: String
    mqttUri: String
    region: String
    hostSettings: HostSettings
}

structure ConnectionSettings {
    @required
    deviceId: String
    @required
    uri: String
    @required
    region: String
}

structure CertRotate {
    @required
    mqttUri: String
    @required
    deviceCert: String
    @required
    region: String
}

enum DeprovisionReason {
    DEPROVISIONED
    EXPIRED
    UNKNOWN
}

structure DeprovisionMessage {
    reason: DeprovisionReason
    //TODO: use timestamp instead?
    time: Integer
}

structure ThumbnailRequest {
    period: Integer
    expires: Integer
    maxSizeKilobyte: Integer
    localPath: String
    remotePath: String
}

structure ThumbnailSubscription {
    @required
    requests: ThumbnailRequestMap
}

map ThumbnailRequestMap {
    key: String
    value: ThumbnailRequest
}

structure LogRequest {
    // TODO: use timestamp?
    expires: Integer
    remotePath: String
}

structure ReportMessage {
    @required
    message: Document
}

structure HostConfig {
    @required
    serviceId: String
    @required
    serviceName: String
    @required
    deviceTypes: StringList
    @required
    thumbnailMaxSizeKB: Integer
    @required
    logFileMaxSizeKB: Integer
    @required
    pairingUrl: String
    @required
    authUrl: String
}

structure Health {
    @required
    state: healthLevel
    @required
    message: String
    @required
    @timestampFormat("date-time")
    timestamp: Timestamp
    componentName: String
}

enum healthLevel {
    HEALTHY,
    DEGRADED,
    CRITICAL
}


structure VersionResponse {
    @required
    version: ProtocolVersion
}