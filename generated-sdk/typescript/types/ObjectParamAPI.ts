import { ResponseContext, RequestContext, HttpFile, HttpInfo } from '../http/http';
import { Configuration, ConfigurationOptions } from '../configuration'
import type { Middleware } from '../middleware';

import { ChannelConfiguration } from '../models/ChannelConfiguration';
import { ChannelState } from '../models/ChannelState';
import { Connection } from '../models/Connection';
import { GetConfigurationResponseContent } from '../models/GetConfigurationResponseContent';
import { IdAndValue } from '../models/IdAndValue';
import { RistCaller } from '../models/RistCaller';
import { RistCallerTransportProtocol } from '../models/RistCallerTransportProtocol';
import { RistListener } from '../models/RistListener';
import { RistListenerTransportProtocol } from '../models/RistListenerTransportProtocol';
import { RouterDeviceConfiguration } from '../models/RouterDeviceConfiguration';
import { SetConfigurationRequestContent } from '../models/SetConfigurationRequestContent';
import { SettingProfile } from '../models/SettingProfile';
import { SrtCaller } from '../models/SrtCaller';
import { SrtCallerTransportProtocol } from '../models/SrtCallerTransportProtocol';
import { SrtListener } from '../models/SrtListener';
import { SrtListenerTransportProtocol } from '../models/SrtListenerTransportProtocol';
import { TransportProtocol } from '../models/TransportProtocol';
import { ZixiCaller } from '../models/ZixiCaller';
import { ZixiCallerTransportProtocol } from '../models/ZixiCallerTransportProtocol';
import { ZixiListener } from '../models/ZixiListener';
import { ZixiListenerTransportProtocol } from '../models/ZixiListenerTransportProtocol';

import { ObservableDefaultApi } from "./ObservableAPI";
import { DefaultApiRequestFactory, DefaultApiResponseProcessor} from "../apis/DefaultApi";

export interface DefaultApiGetConfigurationRequest {
}

export interface DefaultApiSetConfigurationRequest {
    /**
     * 
     * @type SetConfigurationRequestContent
     * @memberof DefaultApisetConfiguration
     */
    setConfigurationRequestContent: SetConfigurationRequestContent
}

export class ObjectDefaultApi {
    private api: ObservableDefaultApi

    public constructor(configuration: Configuration, requestFactory?: DefaultApiRequestFactory, responseProcessor?: DefaultApiResponseProcessor) {
        this.api = new ObservableDefaultApi(configuration, requestFactory, responseProcessor);
    }

    /**
     * @param param the request object
     */
    public getConfigurationWithHttpInfo(param: DefaultApiGetConfigurationRequest = {}, options?: ConfigurationOptions): Promise<HttpInfo<GetConfigurationResponseContent>> {
        return this.api.getConfigurationWithHttpInfo( options).toPromise();
    }

    /**
     * @param param the request object
     */
    public getConfiguration(param: DefaultApiGetConfigurationRequest = {}, options?: ConfigurationOptions): Promise<GetConfigurationResponseContent> {
        return this.api.getConfiguration( options).toPromise();
    }

    /**
     * @param param the request object
     */
    public setConfigurationWithHttpInfo(param: DefaultApiSetConfigurationRequest, options?: ConfigurationOptions): Promise<HttpInfo<void>> {
        return this.api.setConfigurationWithHttpInfo(param.setConfigurationRequestContent,  options).toPromise();
    }

    /**
     * @param param the request object
     */
    public setConfiguration(param: DefaultApiSetConfigurationRequest, options?: ConfigurationOptions): Promise<void> {
        return this.api.setConfiguration(param.setConfigurationRequestContent,  options).toPromise();
    }

}
