import { Resolvers } from "./rest.generated.js";

const resolvers: Resolvers = {
  DataSourceInterface: {
    __resolveType: (dataSource) => {
      switch (dataSource.type) {
        case "aws_cnr": {
          return "AwsDataSource";
        }
        case "azure_tenant": {
          return "AzureTenantDataSource";
        }
        case "azure_cnr": {
          return "AzureSubscriptionDataSource";
        }
        case "gcp_cnr": {
          return "GcpDataSource";
        }
        case "alibaba_cnr": {
          return "AlibabaDataSource";
        }
        case "nebius": {
          return "NebiusDataSource";
        }
        case "databricks": {
          return "DatabricksDataSource";
        }
        case "kubernetes_cnr": {
          return "K8sDataSource";
        }
        case "environment": {
          return "EnvironmentDataSource";
        }
        default: {
          return null;
        }
      }
    },
  },
  Query: {
    dataSource: async (_, { dataSourceId, requestParams }, { dataSources }) => {
      return dataSources.rest.getDataSource(dataSourceId, requestParams);
    },
  },
};

export default resolvers;
