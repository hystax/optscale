import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getAvailablePools, applyAssignmentRules } from "api";
import { GET_AVAILABLE_POOLS, APPLY_ASSIGNMENT_RULES } from "api/restapi/actionTypes";
import ReapplyRulesetForm from "components/ReapplyRulesetForm";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const GET_AVAILABLE_POOLS_PERMISSION = ["MANAGE_POOLS"];

const ReapplyRulesetFormContainer = ({ closeSideModal }) => {
  const { organizationId } = useOrganizationInfo();
  const dispatch = useDispatch();

  const { isLoading: isPoolsLoading, shouldInvoke } = useApiState(GET_AVAILABLE_POOLS, {
    permission: GET_AVAILABLE_POOLS_PERMISSION,
    organizationId
  });
  const { isLoading: isRulesApplyLoading } = useApiState(APPLY_ASSIGNMENT_RULES);

  const onSubmit = (poolId, includeChildren) =>
    dispatch((_, getState) => {
      dispatch(applyAssignmentRules(organizationId, { poolId, includeChildren })).then(() => {
        if (!isError(APPLY_ASSIGNMENT_RULES, getState())) {
          closeSideModal();
        }
      });
    });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAvailablePools(organizationId, { permission: GET_AVAILABLE_POOLS_PERMISSION }));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  return (
    <ReapplyRulesetForm
      onSubmit={onSubmit}
      closeSideModal={closeSideModal}
      pools={pools}
      isSubmitLoading={isRulesApplyLoading}
      isFormLoading={isPoolsLoading}
    />
  );
};

ReapplyRulesetFormContainer.propTypes = {
  closeSideModal: PropTypes.func.isRequired
};

export default ReapplyRulesetFormContainer;
