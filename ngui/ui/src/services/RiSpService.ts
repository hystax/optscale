import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getReservedInstancesBreakdown, getSavingPlansBreakdown } from "api";
import { GET_RESERVED_INSTANCES_BREAKDOWN, GET_SAVING_PLANS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetReservedInstancesBreakdown = (startDate, endDate, dataSourceIds) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_RESERVED_INSTANCES_BREAKDOWN, {});

  const { isLoading, shouldInvoke } = useApiState(GET_RESERVED_INSTANCES_BREAKDOWN, {
    organizationId,
    startDate,
    endDate,
    dataSourceIds
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getReservedInstancesBreakdown(organizationId, { startDate, endDate, dataSourceIds }));
    }
  }, [shouldInvoke, dispatch, organizationId, startDate, endDate, dataSourceIds]);

  return { isLoading, breakdown: apiData };
};

const useGetSavingPlansBreakdown = (startDate, endDate, dataSourceIds) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_SAVING_PLANS_BREAKDOWN, {});

  const { isLoading, shouldInvoke } = useApiState(GET_SAVING_PLANS_BREAKDOWN, {
    organizationId,
    startDate,
    endDate,
    dataSourceIds
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getSavingPlansBreakdown(organizationId, { startDate, endDate, dataSourceIds }));
    }
  }, [shouldInvoke, dispatch, organizationId, startDate, endDate, dataSourceIds]);

  return { isLoading, breakdown: apiData };
};

function RiSpService() {
  return {
    useGetReservedInstancesBreakdown,
    useGetSavingPlansBreakdown
  };
}

export default RiSpService;
