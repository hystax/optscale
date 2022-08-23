import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import RunFinOpsAssessmentForm from "components/RunFinOpsAssessmentForm";
import { SPACING_1 } from "utils/layouts";

const RunReport = ({ onRunReport, isLoadingProps = {} }) => {
  // TODO: common issue on most forms - reportRequestorId is defined as a constant field name in a form, should take it from a single place
  const onSubmit = () => {
    onRunReport({ step: 1 });
  };

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <FormattedMessage
            id="finOpsAssessment.runReportDescription"
            values={{
              p: (chunks) => <p>{chunks}</p>
            }}
          />
        </Typography>
        <RunFinOpsAssessmentForm onSubmit={onSubmit} isLoadingProps={isLoadingProps} />
      </Grid>
    </Grid>
  );
};

RunReport.propTypes = {
  onRunReport: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.object
};

export default RunReport;
