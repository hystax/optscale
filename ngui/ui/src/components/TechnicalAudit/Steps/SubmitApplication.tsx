import ClearOutlinedIcon from "@mui/icons-material/ClearOutlined";
import DoneOutlinedIcon from "@mui/icons-material/DoneOutlined";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Icon from "components/Icon";
import IconButton from "components/IconButton";
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
  hasSuccessfulCodeReportUpload = false,
  isLoadingProps = {},
  setActiveStep
}) => {
  const {
    isGetTechnicalAuditLoading = false,
    isUpdateTechnicalAuditLoading = false,
    isSubmitForAuditLoading = false
  } = isLoadingProps;

  const canSubmit = Object.values(confirmation).every(Boolean) && !hasDataSourcesInProcessing && hasSuccessfulCodeReportUpload;

  const { connectedDataSources = false, uploadedCodeReport = false, completedSurvey = false } = confirmation;

  const completedListDefinition = [
    {
      messageId: "technicalAudit.submitApplicationConnectCloudAccountsAndK8sClusters",
      condition: connectedDataSources,
      stepId: PROVIDE_DATA_STEPS.INFRASTRUCTURE
    },
    {
      messageId: "technicalAudit.submitApplicationWaitForAllDataSourcesInitialExpenseProcessing",
      condition: !hasDataSourcesInProcessing
    },
    {
      messageId: "technicalAudit.submitApplicationUploadSourceCodeStateReport",
      condition: uploadedCodeReport && hasSuccessfulCodeReportUpload,
      stepId: PROVIDE_DATA_STEPS.CODE,
      isLoading: isGetTechnicalAuditLoading
    },
    {
      messageId: "technicalAudit.submitApplicationCompleteSurvey",
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
          <ButtonLoader
            messageId="submit"
            isLoading={isGetTechnicalAuditLoading || isUpdateTechnicalAuditLoading || isSubmitForAuditLoading}
            dataTestId="btn_submit"
            loaderDataTestId="btn_submit_loader"
            variant="contained"
            color="primary"
            onClick={onSubmit}
            disabled={!canSubmit}
          />
        </FormButtonsWrapper>
      </Grid>
    </Grid>
  );
};

export default SubmitApplication;
