import { useDispatch } from "react-redux";
import { SUBMIT_FOR_AUDIT } from "api/restapi/actionTypes";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import TechnicalAuditService from "services/TechnicalAuditService";
import { isError } from "utils/api";
import { isEmpty } from "utils/arrays";
import SubmitApplication from "./SubmitApplication";

const SubmitApplicationContainer = ({
  confirmation,
  onSubmit,
  hasDataSourcesInProcessing,
  isLoadingProps = {},
  setActiveStep
}) => {
  const dispatch = useDispatch();

  const { useSubmitApplication } = TechnicalAuditService();
  const { submit, isSubmitForAuditLoading } = useSubmitApplication();

  const { useGetTechnicalAudit } = OrganizationOptionsService();
  const {
    options: { codeReportFiles = [] }
  } = useGetTechnicalAudit();

  const submitApplication = () =>
    dispatch((_, getState) => {
      submit().then(() => {
        if (!isError(SUBMIT_FOR_AUDIT, getState())) {
          onSubmit({ step: 2 });
        }
      });
    });

  return (
    <SubmitApplication
      onSubmit={submitApplication}
      isLoadingProps={{ ...isLoadingProps, isSubmitForAuditLoading }}
      confirmation={confirmation}
      hasDataSourcesInProcessing={hasDataSourcesInProcessing}
      hasSuccessfulCodeReportUpload={!isEmpty(codeReportFiles)}
      setActiveStep={setActiveStep}
    />
  );
};

export default SubmitApplicationContainer;
