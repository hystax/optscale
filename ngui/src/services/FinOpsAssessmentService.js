import { useDispatch } from "react-redux";
import { submitForAudit } from "api";
import { SUBMIT_FOR_AUDIT } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useSubmitApplication = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(SUBMIT_FOR_AUDIT);

  const submit = () => dispatch(submitForAudit(organizationId));

  return { submit, isSubmitForAuditLoading: isLoading };
};

function FinOpsAssessmentService() {
  return { useSubmitApplication };
}

export default FinOpsAssessmentService;
