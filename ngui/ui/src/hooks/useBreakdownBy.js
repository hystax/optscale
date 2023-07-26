import { useEffect, useMemo } from "react";
import { intl } from "translations/react-intl-config";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY, RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { updateQueryParams } from "utils/network";
import { useReactiveSearchParams } from "./useReactiveSearchParams";

const getBreakdownDefinition = (value, messageId) => ({
  value,
  name: intl.formatMessage({ id: messageId })
});

const serviceNameBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.SERVICE_NAME, "service");

const regionBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.REGION, "region");

const resourceTypeBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.RESOURCE_TYPE, "resourceType");

const dataSourceBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.CLOUD_ACCOUNT_ID, "dataSource");

const ownerBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID, "owner");

const poolBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.POOL_ID, "pool");

const k8sNodeBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NODE, "k8sNode");

const k8sNamespaceBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_NAMESPACE, "k8sNamespace");

const k8sServiceBreakdown = getBreakdownDefinition(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.K8S_SERVICE, "k8sService");

export const breakdowns = Object.freeze([
  serviceNameBreakdown,
  regionBreakdown,
  resourceTypeBreakdown,
  dataSourceBreakdown,
  ownerBreakdown,
  poolBreakdown,
  k8sNodeBreakdown,
  k8sNamespaceBreakdown,
  k8sServiceBreakdown
]);

export const useBreakdownBy = ({ queryParamName }) => {
  const searchParams = useReactiveSearchParams(useMemo(() => [queryParamName], [queryParamName]));

  const breakdownByQueryParameterValue = searchParams[queryParamName];

  const breakdownBy = RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES.includes(breakdownByQueryParameterValue)
    ? breakdowns.find(({ value }) => value === breakdownByQueryParameterValue)
    : serviceNameBreakdown;

  useEffect(() => {
    if (!searchParams[queryParamName]) {
      updateQueryParams({
        [queryParamName]: serviceNameBreakdown.value
      });
    }
  }, [queryParamName, searchParams]);

  const onBreakdownByChange = (newBreakdownByValue) => {
    updateQueryParams({
      [queryParamName]: newBreakdownByValue
    });
  };

  return [breakdownBy, onBreakdownByChange];
};
