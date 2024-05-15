import { useDispatch } from "react-redux";
import { applyAssignmentRules } from "api";
import { APPLY_ASSIGNMENT_RULES } from "api/restapi/actionTypes";
import ReapplyRulesetForm from "components/ReapplyRulesetForm";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const ReapplyRulesetFormContainer = ({ managedPools, closeSideModal }) => {
  const { organizationId } = useOrganizationInfo();
  const dispatch = useDispatch();

  const { isLoading: isRulesApplyLoading } = useApiState(APPLY_ASSIGNMENT_RULES);

  const onSubmit = (poolId, includeChildren) =>
    dispatch((_, getState) => {
      dispatch(applyAssignmentRules(organizationId, { poolId, includeChildren })).then(() => {
        if (!isError(APPLY_ASSIGNMENT_RULES, getState())) {
          closeSideModal();
        }
      });
    });

  return (
    <ReapplyRulesetForm
      onSubmit={onSubmit}
      closeSideModal={closeSideModal}
      managedPools={managedPools}
      isSubmitLoading={isRulesApplyLoading}
    />
  );
};

export default ReapplyRulesetFormContainer;
