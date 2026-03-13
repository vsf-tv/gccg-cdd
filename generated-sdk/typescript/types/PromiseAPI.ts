import { ResponseContext, RequestContext, HttpFile, HttpInfo } from '../http/http';
import { Configuration, PromiseConfigurationOptions, wrapOptions } from '../configuration'
import { PromiseMiddleware, Middleware, PromiseMiddlewareWrapper } from '../middleware';

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
import { ObservableDefaultApi } from './ObservableAPI';

import { DefaultApiRequestFactory, DefaultApiResponseProcessor} from "../apis/DefaultApi";
export class PromiseDefaultApi {
    private api: ObservableDefaultApi

    public constructor(
        configuration: Configuration,
        requestFactory?: DefaultApiRequestFactory,
        responseProcessor?: DefaultApiResponseProcessor
    ) {
        this.api = new ObservableDefaultApi(configuration, requestFactory, responseProcessor);
    }

    /**
     */
    public getConfigurationWithHttpInfo(_options?: PromiseConfigurationOptions): Promise<HttpInfo<GetConfigurationResponseContent>> {
        const observableOptions = wrapOptions(_options);
        const result = this.api.getConfigurationWithHttpInfo(observableOptions);
        return result.toPromise();
    }

    /**
     */
    public getConfiguration(_options?: PromiseConfigurationOptions): Promise<GetConfigurationResponseContent> {
        const observableOptions = wrapOptions(_options);
        const result = this.api.getConfiguration(observableOptions);
        return result.toPromise();
    }

    /**
     * @param setConfigurationRequestContent
     */
    public setConfigurationWithHttpInfo(setConfigurationRequestContent: SetConfigurationRequestContent, _options?: PromiseConfigurationOptions): Promise<HttpInfo<void>> {
        const observableOptions = wrapOptions(_options);
        const result = this.api.setConfigurationWithHttpInfo(setConfigurationRequestContent, observableOptions);
        return result.toPromise();
    }

    /**
     * @param setConfigurationRequestContent
     */
    public setConfiguration(setConfigurationRequestContent: SetConfigurationRequestContent, _options?: PromiseConfigurationOptions): Promise<void> {
        const observableOptions = wrapOptions(_options);
        const result = this.api.setConfiguration(setConfigurationRequestContent, observableOptions);
        return result.toPromise();
    }


}



