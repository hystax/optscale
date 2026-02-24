import BaseClient from "../baseClient.js";
import {
  DataSourceRequestParams,
  MutationUpdateEmployeeEmailsArgs,
  MutationUpdateEmployeeEmailArgs,
  MutationCreateDataSourceArgs,
  MutationUpdateDataSourceArgs,
  MutationUpdateOrganizationArgs,
  MutationCreateOrganizationArgs,
  MutationDeleteOrganizationArgs,
  MutationUpdateOrganizationPerspectivesArgs,
  MutationCreateStripeCheckoutSessionArgs,
  MutationCreateStripeBillingPortalSessionArgs,
  QueryOrganizationPerspectivesArgs,
  QueryOrganizationFeaturesArgs,
  QueryOrganizationConstraintArgs,
  QueryResourceCountBreakdownArgs,
  QueryExpensesDailyBreakdownArgs,
  QueryOrganizationLimitHitsArgs,
  QueryEmployeeEmailsArgs,
  QueryRelevantFlavorsArgs,
  QueryCleanExpensesArgs,
  QueryCloudPoliciesArgs,
  QueryMetaBreakdownArgs,
  QueryAvailableFiltersArgs,
  QueryOrganizationSummaryArgs,
  QueryBillingSubscriptionPlansArgs,
  QueryBillingSubscriptionArgs,
} from "../../graphql/__generated__/types/restapi";
import { getParams } from "../../utils/getParams.js";

class RestApiClient extends BaseClient {
  override baseURL = `${process.env.RESTAPI_ENDPOINT || this.endpoint}/restapi/v2/`;

  async getOrganizations() {
    const organizations = await this.get("organizations");

    return organizations.organizations;
  }

  async getCurrentEmployee(organizationId: string) {
    const path = `organizations/${organizationId}/employees`;

    const currentEmployee = await this.get(path, {
      params: getParams({ current_only: true }),
    });

    return currentEmployee.employees[0];
  }

  async getDataSources(organizationId: string) {
    const path = `organizations/${organizationId}/cloud_accounts`;

    const dataSources = await this.get(path, {
      params: getParams({ details: true }),
    });

    return dataSources.cloud_accounts;
  }

  async getDataSource(dataSourceId: string, requestParams: DataSourceRequestParams) {
    const path = `cloud_accounts/${dataSourceId}`;

    const dataSource = await this.get(path, {
      params: getParams({
        details: requestParams.details,
      }),
    });

    return dataSource;
  }

  async createDataSource(
    organizationId: MutationCreateDataSourceArgs["organizationId"],
    params: MutationCreateDataSourceArgs["params"]
  ) {
    const path = `organizations/${organizationId}/cloud_accounts`;

    const dataSource = await this.post(path, {
      body: {
        name: params.name,
        type: params.type,
        config: {
          ...params.awsRootConfig,
          ...params.awsLinkedConfig,
          ...params.awsAssumedRoleConfig,
          ...params.azureSubscriptionConfig,
          ...params.azureTenantConfig,
          ...params.gcpConfig,
          ...params.gcpTenantConfig,
          ...params.alibabaConfig,
          ...params.nebiusConfig,
          ...params.databricksConfig,
          ...params.k8sConfig,
        },
      },
    });

    return dataSource;
  }

  async updateDataSource(
    dataSourceId: MutationUpdateDataSourceArgs["dataSourceId"],
    params: MutationUpdateDataSourceArgs["params"]
  ) {
    const path = `cloud_accounts/${dataSourceId}`;

    const dataSource = await this.patch(path, {
      body: JSON.stringify({
        name: params.name,
        last_import_at: params.lastImportAt,
        last_import_modified_at: params.lastImportModifiedAt,
        config: {
          ...params.awsRootConfig,
          ...params.awsLinkedConfig,
          ...params.awsAssumedRoleConfig,
          ...params.azureSubscriptionConfig,
          ...params.azureTenantConfig,
          ...params.gcpConfig,
          ...params.gcpTenantConfig,
          ...params.alibabaConfig,
          ...params.nebiusConfig,
          ...params.databricksConfig,
          ...params.k8sConfig,
        },
      }),
    });

    return dataSource;
  }

  async getEmployeeEmails(employeeId: QueryEmployeeEmailsArgs["employeeId"]) {
    const path = `employees/${employeeId}/emails`;

    const emails = await this.get(path);

    return emails.employee_emails;
  }

  async updateEmployeeEmails(
    employeeId: MutationUpdateEmployeeEmailsArgs["employeeId"],
    params: MutationUpdateEmployeeEmailsArgs["params"]
  ) {
    const path = `employees/${employeeId}/emails/bulk`;

    const emails = await this.post(path, {
      body: params,
    });

    const emailIds = [...(params?.enable ?? []), ...(params.disable ?? [])];

    return emails.employee_emails.filter((email) => emailIds.includes(email.id));
  }

  async updateEmployeeEmail(
    employeeId: MutationUpdateEmployeeEmailArgs["employeeId"],
    params: MutationUpdateEmployeeEmailArgs["params"]
  ) {
    const { emailId, action } = params;

    const path = `employees/${employeeId}/emails/bulk`;

    const emails = await this.post(path, {
      body: {
        [action === "enable" ? "enable" : "disable"]: [emailId],
      },
    });

    const email = emails.employee_emails.find((employeeEmail) => employeeEmail.id === emailId);

    return email;
  }

  async deleteDataSource(dataSourceId) {
    const path = `cloud_accounts/${dataSourceId}`;

    return await this.delete(path);
  }

  async getInvitations() {
    const invitations = await this.get("invites");

    return invitations.invites;
  }

  async updateInvitation(invitationId: string, action: string) {
    const path = `invites/${invitationId}`;

    return await this.patch(path, {
      body: JSON.stringify({
        action,
      }),
    });
  }

  async getOrganizationFeatures(organizationId: QueryOrganizationFeaturesArgs["organizationId"]) {
    const path = `organizations/${organizationId}/options/features`;
    const features = await this.get(path);

    const parsedFeatures = JSON.parse(features.value);

    return parsedFeatures;
  }

  async getOrganizationThemeSettings(organizationId: string) {
    const path = `organizations/${organizationId}/options/theme_settings`;
    const settings = await this.get(path);

    const parsedSettings = JSON.parse(settings.value);

    return parsedSettings;
  }

  async updateOrganizationThemeSettings(organizationId, value) {
    const themeSettings = await this.patch(`organizations/${organizationId}/options/theme_settings`, {
      body: {
        value: JSON.stringify(value),
      },
    });

    const parsedThemeSettings = JSON.parse(themeSettings.value);

    return parsedThemeSettings;
  }

  async getOrganizationPerspectives(organizationId: QueryOrganizationPerspectivesArgs["organizationId"]) {
    const path = `organizations/${organizationId}/options/perspectives`;
    const perspectives = await this.get(path);

    const parsedPerspectives = JSON.parse(perspectives.value);

    return parsedPerspectives;
  }

  async updateOrganizationPerspectives(
    organizationId: MutationUpdateOrganizationPerspectivesArgs["organizationId"],
    value: MutationUpdateOrganizationPerspectivesArgs["value"]
  ) {
    const perspectives = await this.patch(`organizations/${organizationId}/options/perspectives`, {
      body: {
        value: JSON.stringify(value),
      },
    });

    const parsedPerspectives = JSON.parse(perspectives.value);

    return parsedPerspectives;
  }

  async createOrganization(organizationName: MutationCreateOrganizationArgs["organizationName"]) {
    return await this.post("organizations", {
      body: {
        name: organizationName,
      },
    });
  }

  async updateOrganization(
    organizationId: MutationUpdateOrganizationArgs["organizationId"],
    params: MutationUpdateOrganizationArgs["params"]
  ) {
    return await this.patch(`organizations/${organizationId}`, {
      body: params,
    });
  }

  async deleteOrganization(organizationId: MutationDeleteOrganizationArgs["organizationId"]) {
    return await this.delete(`organizations/${organizationId}`);
  }

  async getOrganizationConstraint(constraintId: QueryOrganizationConstraintArgs["constraintId"]) {
    const path = `organization_constraints/${constraintId}`;

    const organizationConstraint = await this.get(path);

    return organizationConstraint;
  }

  async getResourceCountBreakdown(
    organizationId: QueryResourceCountBreakdownArgs["organizationId"],
    params: QueryResourceCountBreakdownArgs["params"]
  ) {
    const path = `organizations/${organizationId}/resources_count`;

    const resourceCountBreakdown = await this.get(path, {
      params: getParams(params),
    });

    return resourceCountBreakdown;
  }

  async getMetaBreakdown(organizationId: QueryMetaBreakdownArgs["organizationId"], params: QueryMetaBreakdownArgs["params"]) {
    const path = `organizations/${organizationId}/breakdown_meta`;

    const metaBreakdown = await this.get(path, {
      params: getParams(params),
    });

    return metaBreakdown;
  }

  async getExpensesDailyBreakdown(
    organizationId: QueryExpensesDailyBreakdownArgs["organizationId"],
    params: QueryExpensesDailyBreakdownArgs["params"]
  ) {
    const path = `organizations/${organizationId}/breakdown_expenses`;

    const dailyExpensesBreakdown = await this.get(path, {
      params: getParams(params),
    });

    return dailyExpensesBreakdown;
  }

  async getOrganizationLimitHits(
    organizationId: QueryOrganizationLimitHitsArgs["organizationId"],
    constraintId: QueryOrganizationLimitHitsArgs["constraintId"]
  ) {
    const path = `organizations/${organizationId}/organization_limit_hits`;

    const organizationLimitHits = await this.get(path, {
      params: getParams({
        constraint_id: constraintId,
      }),
    });

    return organizationLimitHits.organization_limit_hits;
  }

  async getRelevantFlavors(
    organizationId: QueryRelevantFlavorsArgs["organizationId"],
    requestParams: QueryRelevantFlavorsArgs["requestParams"]
  ) {
    const path = `organizations/${organizationId}/relevant_flavors`;

    const flavors = await this.get(path, {
      params: getParams(requestParams),
    });

    return flavors;
  }

  async getCleanExpenses(organizationId: QueryCleanExpensesArgs["organizationId"], params: QueryCleanExpensesArgs["params"]) {
    const path = `organizations/${organizationId}/clean_expenses`;

    const cleanExpenses = await this.get(path, {
      params: getParams(params),
    });

    return cleanExpenses;
  }

  async getCloudPolicies(organizationId: QueryCloudPoliciesArgs["organizationId"], params: QueryCloudPoliciesArgs["params"]) {
    const path = `organizations/${organizationId}/cloud_policies`;

    const cloudPolicies = await this.get(path, {
      params: getParams(params),
    });

    return cloudPolicies;
  }

  async getAvailableFilters(
    organizationId: QueryAvailableFiltersArgs["organizationId"],
    params: QueryAvailableFiltersArgs["params"]
  ) {
    const path = `organizations/${organizationId}/available_filters`;

    const availableFilters = await this.get(path, {
      params: getParams(params),
    });

    return availableFilters.filter_values;
  }

  async getBillingSubscriptionPlans(organizationId: QueryBillingSubscriptionPlansArgs["organizationId"]) {
    const path = `organizations/${organizationId}/subscription_plans`;
    const plans = await this.get(path);

    return plans.plans;
  }

  async getBillingSubscription(organizationId: QueryBillingSubscriptionArgs["organizationId"]) {
    const path = `organizations/${organizationId}/subscription`;
    const subscription = await this.get(path);

    return subscription;
  }

  async createStripeCheckoutSession(
    organizationId: MutationCreateStripeCheckoutSessionArgs["organizationId"],
    params: MutationCreateStripeCheckoutSessionArgs["params"]
  ) {
    const path = `organizations/${organizationId}/subscription`;
    const session = await this.patch(path, {
      body: params,
    });

    return session;
  }

  async createStripeBillingPortalSession(organizationId: MutationCreateStripeBillingPortalSessionArgs["organizationId"]) {
    const path = `organizations/${organizationId}/subscription`;
    const session = await this.patch(path, {
      body: {},
    });
    return session;
  }

  async getOrganizationSummary(
    organizationId: QueryOrganizationSummaryArgs["organizationId"],
    params: QueryOrganizationSummaryArgs["params"]
  ) {
    const path = `organizations/${organizationId}/summary`;
    const summary = await this.get(path, {
      params: getParams(params),
    });

    return summary;
  }
}

export default RestApiClient;
