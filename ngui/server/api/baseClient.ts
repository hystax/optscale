import {
  RESTDataSource,
  AugmentedRequest,
  type DataSourceConfig,
  type DataSourceRequest,
  type DataSourceFetchResult,
  type CacheOptions,
} from "@apollo/datasource-rest";
import { FORWARD_RESPONSE_HEADERS } from "../config.js";

class BaseClient extends RESTDataSource {
  private token: string;
  protected endpoint: string;
  private responseHeadersStore?: Map<string, Map<string, string>>;
  private dataSourceName?: string;

  constructor(options: DataSourceConfig, token: string, endpoint: string) {
    super(options);
    this.token = token;
    this.endpoint = endpoint;
  }

  setResponseHeadersStore(store: Map<string, Map<string, string>>, dataSourceName: string) {
    this.responseHeadersStore = store;
    this.dataSourceName = dataSourceName;
  }

  override willSendRequest(_path: string, request: AugmentedRequest) {
    request.headers["authorization"] = `Bearer ${this.token}`;
  }

  override async fetch<TResult>(
    path: string,
    incomingRequest?: DataSourceRequest<CacheOptions>
  ): Promise<DataSourceFetchResult<TResult>> {
    // Call the parent fetch method
    const result = await super.fetch<TResult>(path, incomingRequest);

    // Store only specific headers for forwarding to GraphQL response
    // Namespaced by data source to prevent race conditions
    if (this.responseHeadersStore && this.dataSourceName) {
      let dataSourceHeaders = this.responseHeadersStore.get(this.dataSourceName);
      if (!dataSourceHeaders) {
        dataSourceHeaders = new Map<string, string>();
        this.responseHeadersStore.set(this.dataSourceName, dataSourceHeaders);
      }

      // Store headers for this specific data source
      for (const headerName of FORWARD_RESPONSE_HEADERS) {
        const headerValue = result.response.headers.get(headerName);
        if (headerValue) {
          dataSourceHeaders.set(headerName, headerValue);
        }
      }
    }

    return result;
  }
}

export default BaseClient;
