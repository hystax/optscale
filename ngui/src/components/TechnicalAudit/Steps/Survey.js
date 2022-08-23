import React from "react";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { TECHNICAL_AUDIT_SURVEY } from "urls";
import { SPACING_1 } from "utils/layouts";

const Survey = ({ isConfirmed, onConfirm }) => {
  const { organizationId } = useOrganizationInfo();

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <FormattedMessage
            id="technicalAudit.surveyDescription"
            values={{
              p: (chunks) => <p>{chunks}</p>
            }}
          />
        </Typography>
        <Typography>
          <FormattedMessage
            id="technicalAudit.surveyGoToSurvey"
            values={{
              surveyLink: (chunks) => (
                <Link href={`${TECHNICAL_AUDIT_SURVEY}?organization=${organizationId}`} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <FormControlLabel
          control={<Checkbox data-test-id="checkbox_complete_survey" checked={isConfirmed} onChange={onConfirm} />}
          label={
            <Typography>
              <FormattedMessage id="technicalAudit.surveyCompletionConfirmation" />
            </Typography>
          }
        />
      </Grid>
    </Grid>
  );
};

Survey.propTypes = {
  isConfirmed: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired
};

export default Survey;
