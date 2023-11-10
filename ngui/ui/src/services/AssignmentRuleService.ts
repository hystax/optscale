import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getAssignmentRules } from "api";
import { GET_ASSIGNMENT_RULES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGet = (params = {}) => {
  const dispatch = useDispatch();

  const { poolId } = params;

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ASSIGNMENT_RULES, {
    organizationId,
    poolId
  });

  const {
    apiData: { assignmentRules = {} }
  } = useApiData(GET_ASSIGNMENT_RULES);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAssignmentRules(organizationId, { poolId }));
    }
  }, [shouldInvoke, dispatch, organizationId, poolId]);

  return { isLoading, assignmentRules };
};

function AssignmentRuleService() {
  return { useGet };
}

export default AssignmentRuleService;
