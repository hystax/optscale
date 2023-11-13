import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getAvailableFilters } from "api";
import { GET_AVAILABLE_FILTERS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  START_DATE_FILTER,
  END_DATE_FILTER,
  CLOUD_ACCOUNT_ID_FILTER,
  OWNER_ID_FILTER,
  SERVICE_NAME_FILTER,
  REGION_FILTER,
  RESOURCE_TYPE_FILTER,
  ACTIVE_FILTER,
  AVAILABLE_SAVINGS_FILTER,
  CONSTRAINT_VIOLATED_FILTER,
  K8S_NODE_FILTER,
  TAG_FILTER,
  WITHOUT_TAG_FILTER,
  K8S_NAMESPACE_FILTER,
  POOL_ID_FILTER,
  K8S_SERVICE_FILTER,
  NETWORK_TRAFFIC_FROM_FILTER,
  NETWORK_TRAFFIC_TO_FILTER
} from "utils/constants";

export const mapAvailableFilterKeys = (params) => ({
  pool_id: params[POOL_ID_FILTER],
  cloud_account_id: params[CLOUD_ACCOUNT_ID_FILTER],
  owner_id: params[OWNER_ID_FILTER],
  service_name: params[SERVICE_NAME_FILTER],
  region: params[REGION_FILTER],
  resource_type: params[RESOURCE_TYPE_FILTER],
  active: params[ACTIVE_FILTER],
  recommendations: params[AVAILABLE_SAVINGS_FILTER],
  constraint_violated: params[CONSTRAINT_VIOLATED_FILTER],
  k8s_node: params[K8S_NODE_FILTER],
  tag: params[TAG_FILTER],
  without_tag: params[WITHOUT_TAG_FILTER],
  k8s_namespace: params[K8S_NAMESPACE_FILTER],
  k8s_service: params[K8S_SERVICE_FILTER],
  traffic_from: params[NETWORK_TRAFFIC_FROM_FILTER],
  traffic_to: params[NETWORK_TRAFFIC_TO_FILTER]
});

export const useGet = (params = {}, exceptions) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { filter_values: filters }
  } = useApiData(GET_AVAILABLE_FILTERS, { filter_values: {} });

  const { isLoading, shouldInvoke } = useApiState(GET_AVAILABLE_FILTERS, {
    organizationId,
    start_date: params[START_DATE_FILTER],
    end_date: params[END_DATE_FILTER]
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getAvailableFilters(organizationId, {
          start_date: params[START_DATE_FILTER],
          end_date: params[END_DATE_FILTER]
        })
      );
    }
  }, [dispatch, shouldInvoke, params, organizationId]);

  const filtersWithoutExceptions = exceptions
    ? Object.fromEntries(Object.entries(filters).filter(([filterBackendName]) => !exceptions.includes(filterBackendName)))
    : filters;

  return { isLoading, filters: filtersWithoutExceptions };
};

const useIsLoading = () => {
  const { isLoading } = useApiState(GET_AVAILABLE_FILTERS);

  return isLoading;
};

function AvailableFiltersService() {
  return { useGet, useIsLoading };
}

export default AvailableFiltersService;
