import React from "react";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";

const RunTechnicalAuditForm = ({ onSubmit, isLoadingProps = {} }) => {
  const methods = useForm();
  const { handleSubmit } = methods;

  const { isGetFinOpsAssessmentLoading = false, isUpdateFinOpsAssessmentLoading = false } = isLoadingProps;

  return (
    <FormProvider {...methods}>
      <form data-test-id="start_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormButtonsWrapper>
          <SubmitButtonLoader
            messageId="start"
            isLoading={isGetFinOpsAssessmentLoading || isUpdateFinOpsAssessmentLoading}
            dataTestId="btn_start"
            loaderDataTestId="btn_start_loader"
          />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

RunTechnicalAuditForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetFinOpsAssessmentLoading: PropTypes.bool,
    isUpdateFinOpsAssessmentLoading: PropTypes.bool
  })
};

export default RunTechnicalAuditForm;
