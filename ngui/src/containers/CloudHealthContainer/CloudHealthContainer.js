import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getCloudHealth } from "api";
import { GET_CLOUD_HEALTH } from "api/restapi/actionTypes";
import CloudHealth from "components/CloudHealth";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const CloudHealthContainer = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_CLOUD_HEALTH);

  const { isLoading, shouldInvoke } = useApiState(GET_CLOUD_HEALTH, { organizationId });

  useEffect(() => {
    if (organizationId && shouldInvoke) {
      dispatch(getCloudHealth(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return <CloudHealth isLoading={isLoading} data={apiData} />;
};

export default CloudHealthContainer;
