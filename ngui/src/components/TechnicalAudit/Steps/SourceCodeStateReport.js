import React from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { DropzoneForm } from "components/Dropzone";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import KeyValueLabel from "components/KeyValueLabel";
import { CODECLIMATE, CODECLIMATE_GITLAB_WRAPPER, SEMGREP, SEMGREP_GUIDE, SEMGREP_SETTING, CLOC } from "urls";
import { SPACING_1 } from "utils/layouts";

const FILE_TYPES = ["application/gzip", "application/x-gzip", "application/zip", "application/x-zip-compressed", ""];

const SourceCodeStateReport = ({ isConfirmed, onConfirm, onUpload, isLoadingProps, alreadyUploadedFilesCount = 0 }) => {
  const { isUploadCodeReportLoading = false } = isLoadingProps;

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <FormattedMessage
            id="technicalAudit.sourceCodeStateReportDescription"
            values={{
              p: (chunks) => <p>{chunks}</p>,
              ul: (chunks) => <ul>{chunks}</ul>,
              li: (chunks) => <li>{chunks}</li>,
              i: (chunks) => <i>{chunks}</i>,
              pre: (chunks) => <pre style={{ display: "inline-block", margin: 0 }}>{chunks}</pre>,
              codeClimateLink: (chunks) => (
                <Link href={CODECLIMATE} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              gitLabWrapperLink: (chunks) => (
                <Link href={CODECLIMATE_GITLAB_WRAPPER} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              semgrepLink: (chunks) => (
                <Link href={SEMGREP} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              semgrepGuideLink: (chunks) => (
                <Link href={SEMGREP_GUIDE} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              semgrepSettingLink: (chunks) => (
                <Link href={SEMGREP_SETTING} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              clocLink: (chunks) => (
                <Link href={CLOC} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
      </Grid>
      <Grid item xs={12} sm={8} lg={6} xl={4}>
        <DropzoneForm acceptedFiles={FILE_TYPES} onUpload={onUpload} isLoading={isUploadCodeReportLoading} maxFileSizeMb={10} />
        <KeyValueLabel messageId="alreadyUploadedFiles" value={alreadyUploadedFilesCount} />
        <InlineSeverityAlert
          messageId="technicalAudit.sourceCodeStateReportUploadHint"
          messageValues={{ br: <br /> }}
          messageDataTestId="conditions_help"
        />
      </Grid>
      <Grid item xs={12}>
        <FormControlLabel
          control={<Checkbox data-test-id="checkbox_upload_source_code_report" checked={isConfirmed} onChange={onConfirm} />}
          label={
            <Typography>
              <FormattedMessage id="technicalAudit.sourceCodeStateReportConfirmation" />
            </Typography>
          }
        />
      </Grid>
    </Grid>
  );
};

SourceCodeStateReport.propTypes = {
  isConfirmed: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onUpload: PropTypes.func.isRequired,
  alreadyUploadedFilesCount: PropTypes.number,
  isLoadingProps: PropTypes.shape({
    isGetTechnicalAuditLoading: PropTypes.bool,
    isUpdateTechnicalAuditLoading: PropTypes.bool,
    isUploadCodeReportLoading: PropTypes.bool
  })
};

export default SourceCodeStateReport;
