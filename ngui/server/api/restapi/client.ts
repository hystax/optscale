import BaseClient from "../baseClient.js";
import {
  DataSourceRequestParams,
  UpdateDataSourceInput,
} from "../../graphql/resolvers/restapi.generated.js";

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

  async updateDataSource(dataSourceId, params: UpdateDataSourceInput) {
    const path = `cloud_accounts/${dataSourceId}`;

    const dataSource = await this.patch(path, {
      body: JSON.stringify({
        name: params.name,
        config: {
          ...params.awsRootConfig,
          ...params.awsLinkedConfig,
          ...params.azureSubscriptionConfig,
          ...params.azureTenantConfig,
          ...params.gcpConfig,
          ...params.alibabaConfig,
          ...params.nebiusConfig,
          ...params.databricksConfig,
          ...params.k8sConfig,
        },
      }),
    });

    return dataSource;
  }
}

export default RestClient;
