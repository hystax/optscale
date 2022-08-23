import { useDispatch } from "react-redux";
import { uploadCodeReport, submitForAudit } from "api";
import { UPLOAD_CODE_REPORT, SUBMIT_FOR_AUDIT } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useLastResult } from "hooks/useLastResult";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useUploadCodeReport = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPLOAD_CODE_REPORT);
  const { lastResult: { status } = {} } = useLastResult(UPLOAD_CODE_REPORT);

  const upload = (file) => dispatch(uploadCodeReport(organizationId, file));

  return { upload, isUploadCodeReportLoading: isLoading, uploadStatus: status };
};

export const useSubmitApplication = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(SUBMIT_FOR_AUDIT);

  const submit = () => dispatch(submitForAudit(organizationId));

  return { submit, isSubmitForAuditLoading: isLoading };
};

function TechnicalAuditService() {
  return { useUploadCodeReport, useSubmitApplication };
}

export default TechnicalAuditService;
