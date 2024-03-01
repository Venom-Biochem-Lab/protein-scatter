/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataResponse } from '../models/DataResponse';
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
     * Get Data
     * @param limit
     * @returns DataResponse Successful Response
     * @throws ApiError
     */
    public static getData(
        limit: number,
    ): CancelablePromise<DataResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/data/{limit}',
            path: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
