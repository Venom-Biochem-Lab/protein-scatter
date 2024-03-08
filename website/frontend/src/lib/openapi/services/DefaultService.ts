/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse } from '../models/DataResponse';
import type { InfoVenomeResponse } from '../models/InfoVenomeResponse';
import type { TestResponse } from '../models/TestResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Test
     * @returns TestResponse Successful Response
     * @throws ApiError
     */
    public static test(): CancelablePromise<TestResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
    /**
     * Get Info Venome
     * @returns InfoVenomeResponse Successful Response
     * @throws ApiError
     */
    public static getInfoVenome(): CancelablePromise<InfoVenomeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/info/venome',
        });
    }
    /**
     * Get Data
     * @returns DataResponse Successful Response
     * @throws ApiError
     */
    public static getData(): CancelablePromise<DataResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/data',
        });
    }
}
