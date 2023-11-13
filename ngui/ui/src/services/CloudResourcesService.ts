import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { RESTAPI, getOrganizationCloudResources } from "api";
import { GET_ORGANIZATION_CLOUD_RESOURCES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetOnDemandOrganizationCloudResources = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(GET_ORGANIZATION_CLOUD_RESOURCES);
  const { apiData: resources } = useApiData(GET_ORGANIZATION_CLOUD_RESOURCES, []);

  const getData = useCallback(
    (params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getOrganizationCloudResources(organizationId, params)).then(() => {
            if (!isError(GET_ORGANIZATION_CLOUD_RESOURCES, getState())) {
              const data = getState()?.[RESTAPI]?.[GET_ORGANIZATION_CLOUD_RESOURCES];
              return resolve(data);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { getData, isLoading, resources };
};

function CloudResourcesService() {
  return {
    useGetOnDemandOrganizationCloudResources
  };
}

export default CloudResourcesService;
