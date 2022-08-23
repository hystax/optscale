import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { SUBMIT_FOR_AUDIT } from "api/restapi/actionTypes";
import FinOpsAssessmentService from "services/TechnicalAuditService";
import { isError } from "utils/api";
import SubmitApplication from "./SubmitApplication";

const SubmitApplicationContainer = ({
  confirmation,
  onSubmit,
  hasDataSourcesInProcessing,
  isLoadingProps = {},
  setActiveStep,
  cancelButton
}) => {
  const dispatch = useDispatch();

  const { useSubmitApplication } = FinOpsAssessmentService();
  const { submit, isSubmitForAuditLoading } = useSubmitApplication();

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
      setActiveStep={setActiveStep}
      cancelButton={cancelButton}
    />
  );
};

SubmitApplicationContainer.propTypes = {
  confirmation: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  hasDataSourcesInProcessing: PropTypes.bool,
  isLoadingProps: PropTypes.object,
  setActiveStep: PropTypes.func,
  cancelButton: PropTypes.node
};

export default SubmitApplicationContainer;
