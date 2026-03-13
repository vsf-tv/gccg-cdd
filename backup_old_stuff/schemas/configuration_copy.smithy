$version: "2"

namespace com.example.configuration
use aws.protocols#restJson1

@restJson1
service ConfigurationService {
    version: "1.0"
    operations: [GetConfiguration, SetConfiguration]
}

@readonly
@http(method: "GET", uri: "/get_configuration")
operation GetConfiguration {
    output: GetConfigurationOutput
}

@idempotent
@http(method: "PUT", uri: "/report_actual_configuration")
operation SetConfiguration {
    input: SetConfigurationInput
}

structure GetConfigurationOutput {
    @required
    configuration: RouterDeviceConfiguration
}

structure SetConfigurationInput {
    @required
    configuration: RouterDeviceConfiguration
}

structure RouterDeviceConfiguration {
@required
channels: ChannelConfigurationList
}

list ChannelConfigurationList {
member: ChannelConfiguration
}

structure ChannelConfiguration {
@required
id: String,
@required
state: ChannelState,
settings: IdAndValueList,
settingProfile: SettingProfile,
connection: Connection
}

list IdAndValueList {
member: IdAndValue
}

structure SettingProfile {
@required
id: String
}

structure IdAndValue {
@required
id: String,
@required
value: String
}

structure Connection {
transportProtocol: TransportProtocol
}

enum ChannelState {
ACTIVE = "ACTIVE"
IDLE = "IDLE"
}

union TransportProtocol {
srtListener: SrtListenerTransportProtocol,
srtCaller: SrtCallerTransportProtocol,
ristListener: RistListenerTransportProtocol,
ristCaller: RistCallerTransportProtocol,
zixiListener: ZixiListenerTransportProtocol,
zixiCaller: ZixiCallerTransportProtocol
}

structure SrtListenerTransportProtocol {
streamId: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}

structure SrtCallerTransportProtocol {
@required
streamId: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}

structure RistListenerTransportProtocol {
streamId: String,
@required
mode: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}

structure RistCallerTransportProtocol {
@required
streamId: String,
@required
mode: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}

structure ZixiListenerTransportProtocol {
@required
streamId: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}

structure ZixiCallerTransportProtocol {
@required
streamId: String,
@required
ip: String,
@required
port: Integer,
@required
latencyMs: Integer,
}
