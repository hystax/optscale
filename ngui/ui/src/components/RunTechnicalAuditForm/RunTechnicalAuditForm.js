import React from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useToggle } from "hooks/useToggle";
import { ReportRequestorIdField } from "./FormElements";

const RunTechnicalAuditForm = ({ onSubmit, isLoadingProps = {} }) => {
  const [isConfirmed, setIsConfirmed] = useToggle(false);

  const { isDemo } = useOrganizationInfo();

  const methods = useForm();
  const { handleSubmit } = methods;

  const { isGetTechnicalAuditLoading = false, isUpdateTechnicalAuditLoading = false } = isLoadingProps;

  return (
    <FormProvider {...methods}>
      <form data-test-id="start_form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <ReportRequestorIdField />
        <FormControlLabel
          control={<Checkbox data-test-id="checkbox_start_report" checked={isConfirmed} onChange={setIsConfirmed} />}
          label={
            <Typography>
              <FormattedMessage id="technicalAudit.runAuditConfirmation" />
            </Typography>
          }
        />
        <FormButtonsWrapper>
          <SubmitButtonLoader
            messageId="start"
            isLoading={isGetTechnicalAuditLoading || isUpdateTechnicalAuditLoading}
            dataTestId="btn_start"
            loaderDataTestId="btn_start_loader"
            disabled={!isConfirmed || isDemo}
            tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
          />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

RunTechnicalAuditForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetTechnicalAuditLoading: PropTypes.bool,
    isUpdateTechnicalAuditLoading: PropTypes.bool
  })
};

export default RunTechnicalAuditForm;
