import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import { SPACING_1 } from "utils/layouts";

const PlanSubmission = () => {
  const tableData = useMemo(
    () => [
      {
        action: <FormattedMessage id="technicalAudit.planSubmissionConnectDataSourcesAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: "30-60" }} />,
        recommendedJobTitle: <FormattedMessage id="opsDevOpsEngineer" />
      },
      {
        action: <FormattedMessage id="technicalAudit.planSubmissionConnectJiraAndCiCdAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: 30 }} />,
        recommendedJobTitle: <FormattedMessage id="opsDevOpsEngineer" />
      },
      {
        action: <FormattedMessage id="technicalAudit.planSubmissionSourceCodeStateAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: 30 }} />,
        recommendedJobTitle: <FormattedMessage id="opsDevOpsEngineer" />
      },
      {
        action: <FormattedMessage id="technicalAudit.planSubmissionSurveyAction" />,
        averageDuration: <FormattedMessage id="{value}minutes" values={{ value: 30 }} />,
        recommendedJobTitle: <FormattedMessage id="Cto" />
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
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <FormattedMessage
            id="technicalAudit.planSubmissionDetails"
            values={{
              p: (chunks) => <p>{chunks}</p>
            }}
          />
        </Typography>
      </Grid>
    </Grid>
  );
};

export default PlanSubmission;
