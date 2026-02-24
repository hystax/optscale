import { JSONObjectResolver } from "graphql-scalars";
import { Resolvers } from "../__generated__/types/restapi";

const resolvers: Resolvers = {
  JSONObject: JSONObjectResolver,

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
        case "gcp_tenant": {
          return "GcpTenantDataSource";
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
      return dataSources.restapi.getDataSource(dataSourceId, requestParams);
    },
    employeeEmails: async (_, { employeeId }, { dataSources }) => {
      return dataSources.restapi.getEmployeeEmails(employeeId);
    },
    organizations: async (_, __, { dataSources }) => {
      return dataSources.restapi.getOrganizations();
    },
    currentEmployee: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getCurrentEmployee(organizationId);
    },
    dataSources: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getDataSources(organizationId);
    },
    invitations: async (_, __, { dataSources }) => {
      return dataSources.restapi.getInvitations();
    },
    organizationFeatures: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getOrganizationFeatures(organizationId);
    },
    organizationThemeSettings: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getOrganizationThemeSettings(organizationId);
    },
    organizationPerspectives: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getOrganizationPerspectives(organizationId);
    },
    organizationConstraint: async (_, { constraintId }, { dataSources }) => {
      return dataSources.restapi.getOrganizationConstraint(constraintId);
    },
    resourceCountBreakdown: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getResourceCountBreakdown(organizationId, params);
    },
    expensesDailyBreakdown: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getExpensesDailyBreakdown(organizationId, params);
    },
    organizationLimitHits: async (_, { organizationId, constraintId }, { dataSources }) => {
      return dataSources.restapi.getOrganizationLimitHits(organizationId, constraintId);
    },
    relevantFlavors: async (_, { organizationId, requestParams }, { dataSources }) => {
      return dataSources.restapi.getRelevantFlavors(organizationId, requestParams);
    },
    cleanExpenses: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getCleanExpenses(organizationId, params);
    },
    cloudPolicies: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getCloudPolicies(organizationId, params);
    },
    metaBreakdown: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getMetaBreakdown(organizationId, params);
    },
    availableFilters: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getAvailableFilters(organizationId, params);
    },
    billingSubscriptionPlans: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getBillingSubscriptionPlans(organizationId);
    },
    billingSubscription: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.getBillingSubscription(organizationId);
    },
    organizationSummary: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.getOrganizationSummary(organizationId, params);
    },
  },
  Mutation: {
    createDataSource: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.createDataSource(organizationId, params);
    },
    updateDataSource: async (_, { dataSourceId, params }, { dataSources }) => {
      return dataSources.restapi.updateDataSource(dataSourceId, params);
    },
    updateEmployeeEmails: async (_, { employeeId, params }, { dataSources }) => {
      return dataSources.restapi.updateEmployeeEmails(employeeId, params);
    },
    updateEmployeeEmail: async (_, { employeeId, params }, { dataSources }) => {
      return dataSources.restapi.updateEmployeeEmail(employeeId, params);
    },
    deleteDataSource: async (_, { dataSourceId }, { dataSources }) => {
      return dataSources.restapi.deleteDataSource(dataSourceId);
    },
    createOrganization: async (_, { organizationName }, { dataSources }) => {
      return dataSources.restapi.createOrganization(organizationName);
    },
    updateOrganization: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.updateOrganization(organizationId, params);
    },
    deleteOrganization: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.deleteOrganization(organizationId);
    },
    updateInvitation: async (_, { invitationId, action }, { dataSources }) => {
      return dataSources.restapi.updateInvitation(invitationId, action);
    },
    updateOrganizationThemeSettings: async (_, { organizationId, value }, { dataSources }) => {
      return dataSources.restapi.updateOrganizationThemeSettings(organizationId, value);
    },
    updateOrganizationPerspectives: async (_, { organizationId, value }, { dataSources }) => {
      return dataSources.restapi.updateOrganizationPerspectives(organizationId, value);
    },
    createStripeCheckoutSession: async (_, { organizationId, params }, { dataSources }) => {
      return dataSources.restapi.createStripeCheckoutSession(organizationId, params);
    },
    createStripeBillingPortalSession: async (_, { organizationId }, { dataSources }) => {
      return dataSources.restapi.createStripeBillingPortalSession(organizationId);
    },
  },
};

export default resolvers;
