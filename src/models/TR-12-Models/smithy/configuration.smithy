$version: "2"

namespace com.example.cdd.configuration
use com.example.cdd.common#ChannelState
use com.example.cdd.common#Health
use com.example.cdd.common#IdAndValueList

structure DeviceConfiguration {
    @required
    channels: ChannelConfigurationList
    simpleSettings: IdAndValueList
}

list ChannelConfigurationList {
    member: ChannelConfiguration
}

structure ChannelConfiguration {
    @required
    id: String
    @required
    state: ChannelState
    settings: SettingsChoice
    connection: Connection
    health: Health
}

union SettingsChoice {
    simpleSettings: IdAndValueList,
    profile: SettingProfile
}

union RistStreamIdentifier {
    synchronizationSource: Integer
    streamId: String
}

structure SettingProfile {
    @required
    id: String
}

structure Connection {
    transportProtocol: TransportProtocol
}

@length(min: 32, max: 32)
@pattern("^[a-fA-F0-9]+$")
@documentation("A 32-character hexadecimal string.")
string Hex32

@length(min: 64, max: 64)
@pattern("^[a-fA-F0-9]+$")
@documentation("A 64-character hexadecimal string.")
string Hex64

structure DeviceEncryptionAes128 {
    @required
    passcode: Hex32
}

structure DeviceEncryptionAes256 {
    @required
    passcode: Hex64
}

union DeviceEncryption {
    aes128: DeviceEncryptionAes128
    aes256: DeviceEncryptionAes256
}

union TransportProtocol {
    srtListener: SrtListenerTransportProtocol
    srtCaller: SrtCallerTransportProtocol
    ristListener: RistListenerTransportProtocol
    ristCaller: RistCallerTransportProtocol
    zixiListener: ZixiListenerTransportProtocol
    zixiCaller: ZixiCallerTransportProtocol
}

structure SrtListenerTransportProtocol {
    streamId: String
    @required
    @range(min: 1024, max: 65535)
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
    interface: String
}

structure SrtCallerTransportProtocol {
    streamId: String
    @required
    ip: String
    @required
    @range(min: 1, max: 65535)
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
}

structure RistListenerTransportProtocol {
    streamId: RistStreamIdentifier
    @required
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
    interface: String
}

structure RistCallerTransportProtocol {
    streamId: RistStreamIdentifier
    @required
    ip: String
    @required
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
}

structure ZixiListenerTransportProtocol {
    @required
    streamId: String
    @required
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
    interface: String
}

structure ZixiCallerTransportProtocol {
    @required
    streamId: String
    @required
    ip: String
    @required
    port: Integer
    @required
    @default(3000)
    minimumLatencyMilliseconds: Integer
    encryption: DeviceEncryption
}
