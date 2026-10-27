import type { ApolloServerPlugin } from "@apollo/server";
import type { ContextValue } from "../server.js";

/**
 * Plugin to forward response headers from REST API data sources to GraphQL client
 * Headers are only prefixed with x-{dataSourceName}- if they would conflict with existing response headers
 * Example: If GraphQL response already has 'etag', forwarded etag becomes 'x-restapi-etag'
 */
export const responseHeadersPlugin: ApolloServerPlugin<ContextValue> = {
  async requestDidStart() {
    return {
      async willSendResponse({ response, contextValue }) {
        // Forward headers captured from REST API responses
        if (contextValue.responseHeaders && response.http) {
          // Collect all original response headers that already exist
          const existingHeaders = new Set<string>();
          response.http.headers.forEach((_, key) => {
            existingHeaders.add(key.toLowerCase());
          });

          contextValue.responseHeaders.forEach((dataSourceHeaders, dataSourceName) => {
            dataSourceHeaders.forEach((value, headerName) => {
              // Only add x-{dataSourceName}- prefix if header would conflict with existing response header
              const needsPrefix = existingHeaders.has(headerName.toLowerCase());
              const prefixedHeaderName = needsPrefix ? `x-${dataSourceName}-${headerName}` : headerName;

              if (response.http) {
                response.http.headers.set(prefixedHeaderName, value);
              }
            });
          });
        }
      },
    };
  },
};
