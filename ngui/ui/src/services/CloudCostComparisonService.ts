import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getRelevantFlavors } from "api";
import { GET_RELEVANT_FLAVORS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(GET_RELEVANT_FLAVORS);

  const {
    apiData: { flavors: sizes = [], errors = {} }
  } = useApiData(GET_RELEVANT_FLAVORS);

  const onGet = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(getRelevantFlavors(organizationId, params)).then(() => {
          if (!isError(GET_RELEVANT_FLAVORS, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { isLoading, sizes, errors, onGet };
};

const useGet = (params) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_RELEVANT_FLAVORS, { organizationId, params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRelevantFlavors(organizationId, params));
    }
  }, [dispatch, organizationId, params, shouldInvoke]);

  const {
    apiData: { flavors: sizes = [], errors = {} }
  } = useApiData(GET_RELEVANT_FLAVORS);

  return { isLoading, sizes, errors };
};

function CloudCostComparisonService() {
  return { useGet, useGetOnDemand };
}

export default CloudCostComparisonService;
