import BaseClient from "../baseClient.js";
import { DataSourceRequestParams } from "../../graphql/resolvers/rest.generated.js";

class RestClient extends BaseClient {
  override baseURL = `${
    process.env.REST_ENDPOINT || this.endpoint
  }/restapi/v2/`;

  async getDataSource(
    dataSourceId: string,
    requestParams: DataSourceRequestParams
  ) {
    const path = `cloud_accounts/${dataSourceId}?details=${requestParams.details}`;

    const dataSource = await this.get(path);

    return dataSource;
  }
}

export default RestClient;
