import { ResponseContext, RequestContext, HttpFile, HttpInfo } from '../http/http';
import { Configuration, ConfigurationOptions, mergeConfiguration } from '../configuration'
import type { Middleware } from '../middleware';
import { Observable, of, from } from '../rxjsStub';
import {mergeMap, map} from  '../rxjsStub';
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

import { DefaultApiRequestFactory, DefaultApiResponseProcessor} from "../apis/DefaultApi";
export class ObservableDefaultApi {
    private requestFactory: DefaultApiRequestFactory;
    private responseProcessor: DefaultApiResponseProcessor;
    private configuration: Configuration;

    public constructor(
        configuration: Configuration,
        requestFactory?: DefaultApiRequestFactory,
        responseProcessor?: DefaultApiResponseProcessor
    ) {
        this.configuration = configuration;
        this.requestFactory = requestFactory || new DefaultApiRequestFactory(configuration);
        this.responseProcessor = responseProcessor || new DefaultApiResponseProcessor();
    }

    /**
     */
    public getConfigurationWithHttpInfo(_options?: ConfigurationOptions): Observable<HttpInfo<GetConfigurationResponseContent>> {
        const _config = mergeConfiguration(this.configuration, _options);

        const requestContextPromise = this.requestFactory.getConfiguration(_config);
        // build promise chain
        let middlewarePreObservable = from<RequestContext>(requestContextPromise);
        for (const middleware of _config.middleware) {
            middlewarePreObservable = middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => middleware.pre(ctx)));
        }

        return middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => _config.httpApi.send(ctx))).
            pipe(mergeMap((response: ResponseContext) => {
                let middlewarePostObservable = of(response);
                for (const middleware of _config.middleware.reverse()) {
                    middlewarePostObservable = middlewarePostObservable.pipe(mergeMap((rsp: ResponseContext) => middleware.post(rsp)));
                }
                return middlewarePostObservable.pipe(map((rsp: ResponseContext) => this.responseProcessor.getConfigurationWithHttpInfo(rsp)));
            }));
    }

    /**
     */
    public getConfiguration(_options?: ConfigurationOptions): Observable<GetConfigurationResponseContent> {
        return this.getConfigurationWithHttpInfo(_options).pipe(map((apiResponse: HttpInfo<GetConfigurationResponseContent>) => apiResponse.data));
    }

    /**
     * @param setConfigurationRequestContent
     */
    public setConfigurationWithHttpInfo(setConfigurationRequestContent: SetConfigurationRequestContent, _options?: ConfigurationOptions): Observable<HttpInfo<void>> {
        const _config = mergeConfiguration(this.configuration, _options);

        const requestContextPromise = this.requestFactory.setConfiguration(setConfigurationRequestContent, _config);
        // build promise chain
        let middlewarePreObservable = from<RequestContext>(requestContextPromise);
        for (const middleware of _config.middleware) {
            middlewarePreObservable = middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => middleware.pre(ctx)));
        }

        return middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => _config.httpApi.send(ctx))).
            pipe(mergeMap((response: ResponseContext) => {
                let middlewarePostObservable = of(response);
                for (const middleware of _config.middleware.reverse()) {
                    middlewarePostObservable = middlewarePostObservable.pipe(mergeMap((rsp: ResponseContext) => middleware.post(rsp)));
                }
                return middlewarePostObservable.pipe(map((rsp: ResponseContext) => this.responseProcessor.setConfigurationWithHttpInfo(rsp)));
            }));
    }

    /**
     * @param setConfigurationRequestContent
     */
    public setConfiguration(setConfigurationRequestContent: SetConfigurationRequestContent, _options?: ConfigurationOptions): Observable<void> {
        return this.setConfigurationWithHttpInfo(setConfigurationRequestContent, _options).pipe(map((apiResponse: HttpInfo<void>) => apiResponse.data));
    }

}
