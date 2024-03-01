export * from "./openapi";
export { DefaultService as Backend } from "./openapi";
import { OpenAPI } from "./openapi";

export const BACKEND_URL = "http://0.0.0.0:8000";
OpenAPI.BASE = BACKEND_URL;
