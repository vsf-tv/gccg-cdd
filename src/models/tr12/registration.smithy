$version: "2"

namespace com.example.cdd.registration
use com.example.cdd.common#ChannelType
use com.example.cdd.common#SupportedProtocol
use com.example.cdd.common#StringList

structure DeviceRegistration {
    @required
    channels: ChannelList
    simpleSettings: SettingsList
    thumbnails: ThumbnailList
}

list ChannelList {
    member: Channel
}

structure Channel {
    @required
    name: String
    @required
    id: String,
    channelType: ChannelType,
    simpleSettings: SettingsList,
    profiles: ProfileList,
    connectionProtocols: ProtocolList
}

list SettingsList {
    member: Setting
}

structure Setting {
    @required
    id: String
    @required
    name: String
    @required
    info: String
    enums: EnumValues
    ranges: RangeValues
}

structure EnumValues {
    @required
    values: StringList
    @required
    defaultValue: String
}

structure RangeValues {
    @required
    min: Float
    @required
    max: Float
    @required
    defaultValue: Float
}

list ProfileList {
    member: ProfileDefinition
}

structure ProfileDefinition {
    @required
    name: String
    @required
    id: String
    @required
    info: String
}

list ProtocolList {
    member: SupportedProtocol
}

list ThumbnailList {
    member: Thumbnail
}

structure Thumbnail {
    @required
    name: String
    @required
    id: String
    @required
    localPath: String
}