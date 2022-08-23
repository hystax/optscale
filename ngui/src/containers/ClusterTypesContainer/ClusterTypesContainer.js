import React, { useEffect, useCallback } from "react";
import { useDispatch } from "react-redux";
import { getClusterTypes as getClusterTypesAction, updateClusterTypePriority } from "api";
import { GET_CLUSTER_TYPES, UPDATE_CLUSTER_TYPE_PRIORITY } from "api/restapi/actionTypes";
import ClusterTypes from "components/ClusterTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const ClusterTypesContainer = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { clusterTypes = [] }
  } = useApiData(GET_CLUSTER_TYPES);

  const { isLoading: isGetClusterTypesLoading, shouldInvoke } = useApiState(GET_CLUSTER_TYPES, organizationId);

  const getClusterTypes = useCallback(() => dispatch(getClusterTypesAction(organizationId)), [dispatch, organizationId]);

  const { isLoading: isUpdateClusterTypePriorityLoading } = useApiState(UPDATE_CLUSTER_TYPE_PRIORITY);

  useEffect(() => {
    if (shouldInvoke) {
      getClusterTypes();
    }
  }, [dispatch, getClusterTypes, organizationId, shouldInvoke]);

  const updatePriority = (clusterTypeId, action) => {
    dispatch(updateClusterTypePriority(clusterTypeId, action));
  };

  return (
    <ClusterTypes
      isLoading={isGetClusterTypesLoading || isUpdateClusterTypePriorityLoading}
      clusterTypes={clusterTypes}
      onUpdatePriority={updatePriority}
    />
  );
};

export default ClusterTypesContainer;
