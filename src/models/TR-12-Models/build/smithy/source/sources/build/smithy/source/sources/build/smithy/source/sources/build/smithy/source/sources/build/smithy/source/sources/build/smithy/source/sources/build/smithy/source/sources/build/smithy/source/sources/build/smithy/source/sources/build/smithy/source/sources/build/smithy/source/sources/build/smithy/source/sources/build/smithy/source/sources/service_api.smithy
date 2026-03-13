$version: "2"

namespace com.example.cdd.internal

use aws.protocols#restJson1
use com.example.cdd.common#HostSettings
use com.example.cdd.common#PairRequest
use com.example.cdd.common#PairResponse
use com.example.cdd.common#AuthRequest
use com.example.cdd.common#AuthResponse
use com.example.cdd.common#CertRotate
use com.example.cdd.common#DeprovisionMessage
use com.example.cdd.common#ThumbnailSubscription
use com.example.cdd.common#LogRequest
use com.example.cdd.common#HostConfig
use com.example.cdd.common#VersionResponse

@restJson1
service HostServiceApi {
    version: "1.0"
    operations: [
        Pair,
        Authenticate,
        // Marker operations to generate MQTT payload models
        RotateCertificates,
        DeprovisionDevice,
        RequestThumbnail,
        RequestLog,
        GetHostConfig,
        GetVersion
    ]
}

@http(method: "POST", uri: "/pair")
operation Pair {
    input: PairRequest
    output: PairResponse
}

@http(method: "POST", uri: "/authenticate")
operation Authenticate {
    input: AuthRequest
    output: AuthResponse
}

// Marker operations for MQTT payloads - not actual REST endpoints
@http(method: "POST", uri: "/internal/rotate-certs")
operation RotateCertificates {
    input: CertRotate
}

@http(method: "POST", uri: "/internal/deprovision")
operation DeprovisionDevice {
    input: DeprovisionMessage
}

@http(method: "POST", uri: "/internal/thumbnail")
operation RequestThumbnail {
    input: ThumbnailSubscription
}

@http(method: "POST", uri: "/internal/log")
operation RequestLog {
    input: LogRequest
}

@http(method: "GET", uri: "/internal/host-config")
operation GetHostConfig {
    output: HostConfig
}

@http(method: "GET", uri: "/internal/version")
operation GetVersion {
    output: VersionResponse
}
