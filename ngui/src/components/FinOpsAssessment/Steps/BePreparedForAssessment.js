import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import { SPACING_1 } from "utils/layouts";

const BePreparedForAssessment = () => {
  const tableData = useMemo(
    () => [
      {
        action: <FormattedMessage id="finOpsAssessment.bePreparedForAssessmentConnectDataSourcesAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: "30-60" }} />,
        recommendedJobTitle: <FormattedMessage id="opsDevOpsEngineer" />
      },
      {
        action: <FormattedMessage id="finOpsAssessment.bePreparedForAssessmentCompleteFinOpsMaturitySurveyAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: 30 }} />,
        recommendedJobTitle: <FormattedMessage id="finOpsLeader" />
      },
      {
        action: <FormattedMessage id="finOpsAssessment.bePreparedForAssessmentReviewByExpertAction" />,
        averageDuration: <FormattedMessage id="{value}businessDays" values={{ value: "1-2" }} />,
        recommendedJobTitle: <FormattedMessage id="hystaxCertifiedExpert" />
      }
    ],
    []
  );

  const columns = useMemo(
    () => [
      {
        Header: <FormattedMessage id="action" />,
        accessor: "action"
      },
      {
        Header: <FormattedMessage id="averageDuration" />,
        accessor: "averageDuration"
      },
      {
        Header: <FormattedMessage id="recommendedJobTitle" />,
        accessor: "recommendedJobTitle"
      }
    ],
    []
  );

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12} lg={12} xl={8}>
        <Table data={tableData} columns={columns} />
      </Grid>
      <Grid item xs={12}>
        <Typography component="div">
          <FormattedMessage id="finOpsAssessment.bePreparedForAssessmentDetails" />
        </Typography>
      </Grid>
    </Grid>
  );
};

export default BePreparedForAssessment;
