/**
 * Server configuration constants
 */

/**
 * HTTP headers to forward from REST API responses to GraphQL client responses
 * Add any headers here that should be passed through from backend services
 */
const FORWARD_RESPONSE_HEADERS_ARRAY = ["x-trace-id", "etag"] as const;

/**
 * Set for O(1) lookup performance when checking headers
 */
export const FORWARD_RESPONSE_HEADERS = new Set(FORWARD_RESPONSE_HEADERS_ARRAY);

/**
 * Type helper for the forwarded headers
 */
export type ForwardedHeader = (typeof FORWARD_RESPONSE_HEADERS_ARRAY)[number];
