import {
  RESTDataSource,
  AugmentedRequest,
  type DataSourceConfig,
} from "@apollo/datasource-rest";

class BaseClient extends RESTDataSource {
  private token: string;
  protected endpoint: string;

  constructor(options: DataSourceConfig, token: string, endpoint: string) {
    super(options);
    this.token = token;
    this.endpoint = endpoint;
  }

  override willSendRequest(_path: string, request: AugmentedRequest) {
    request.headers["authorization"] = `Bearer ${this.token}`;
  }
}

export default BaseClient;
