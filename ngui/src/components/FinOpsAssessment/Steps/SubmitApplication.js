import React from "react";
import ClearOutlinedIcon from "@mui/icons-material/ClearOutlined";
import DoneOutlinedIcon from "@mui/icons-material/DoneOutlined";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Icon from "components/Icon";
import IconButton from "components/IconButton";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { REGISTER } from "urls";
import { PROVIDE_DATA_STEPS } from "utils/constants";
import { SPACING_1 } from "utils/layouts";

const InfoIcon = ({ isLoading, condition }) =>
  isLoading ? (
    <CircularProgress size={20} />
  ) : (
    <Icon icon={condition ? DoneOutlinedIcon : ClearOutlinedIcon} color={condition ? "success" : "error"} />
  );

const GoToButton = ({ setActiveStep, stepId }) => (
  <IconButton
    style={{ position: "absolute", top: "50%", transform: "translate(0, -50%)" }}
    icon={<ExitToAppOutlinedIcon />}
    onClick={() => setActiveStep(stepId)}
  />
);

const SubmitApplication = ({
  confirmation,
  onSubmit,
  hasDataSourcesInProcessing = false,
  isLoadingProps = {},
  setActiveStep,
  cancelButton
}) => {
  const {
    isGetFinOpsAssessmentLoading = false,
    isUpdateFinOpsAssessmentLoading = false,
    isSubmitForAuditLoading = false
  } = isLoadingProps;

  const navigate = useNavigate();

  const { isDemo } = useOrganizationInfo();

  const canSubmit = Object.values(confirmation).every(Boolean) && !hasDataSourcesInProcessing;

  const { connectedDataSources = false, completedSurvey = false } = confirmation;

  const completedListDefinition = [
    {
      messageId: "finOpsAssessment.submitApplicationConnectCloudAccountsAndK8sClusters",
      condition: connectedDataSources,
      stepId: PROVIDE_DATA_STEPS.INFRASTRUCTURE
    },
    {
      messageId: "finOpsAssessment.submitApplicationWaitForAllDataSourcesInitialExpenseProcessing",
      condition: !hasDataSourcesInProcessing
    },
    {
      messageId: "finOpsAssessment.submitApplicationCompleteSurvey",
      condition: completedSurvey,
      stepId: PROVIDE_DATA_STEPS.SURVEY
    }
  ];

  return (
    <Grid container spacing={SPACING_1}>
      {completedListDefinition.map(({ messageId, condition, stepId, isLoading }) => (
        <Grid item xs={12} key={stepId || messageId}>
          <Box display="flex" alignItems="center">
            <InfoIcon isLoading={isLoading} condition={condition} />
            <Typography style={{ position: "relative" }}>
              <FormattedMessage id={messageId} />
              {!condition && stepId && <GoToButton setActiveStep={setActiveStep} stepId={stepId} />}
            </Typography>
          </Box>
        </Grid>
      ))}
      <Grid item xs={12}>
        <FormButtonsWrapper>
          {cancelButton}
          {isDemo ? (
            <Button
              dataTestId="btn_sign_up_to_proceed"
              color="primary"
              variant="contained"
              messageId="signUpToProceed"
              onClick={() => navigate(REGISTER)}
            />
          ) : (
            <ButtonLoader
              messageId="submit"
              isLoading={isGetFinOpsAssessmentLoading || isUpdateFinOpsAssessmentLoading || isSubmitForAuditLoading}
              dataTestId="btn_submit"
              loaderDataTestId="btn_submit_loader"
              variant="contained"
              color="primary"
              onClick={onSubmit}
              disabled={!canSubmit}
            />
          )}
        </FormButtonsWrapper>
      </Grid>
    </Grid>
  );
};

SubmitApplication.propTypes = {
  confirmation: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  hasDataSourcesInProcessing: PropTypes.bool,
  isLoadingProps: PropTypes.shape({
    isGetFinOpsAssessmentLoading: PropTypes.bool,
    isUpdateFinOpsAssessmentLoading: PropTypes.bool,
    isSubmitForAuditLoading: PropTypes.bool
  }),
  setActiveStep: PropTypes.func.isRequired,
  cancelButton: PropTypes.node
};

export default SubmitApplication;
