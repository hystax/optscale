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
        action: "technicalAudit.planSubmissionConnectDataSourcesAction",
        averageDuration: {
          messageId: "{value}minutes",
          values: { value: "30-60" }
        },
        recommendedJobTitle: "opsDevOpsEngineer"
      },
      {
        action: "technicalAudit.planSubmissionConnectJiraAndCiCdAction",
        averageDuration: {
          messageId: "{value}minutes",
          values: { value: 30 }
        },
        recommendedJobTitle: "opsDevOpsEngineer"
      },
      {
        action: "technicalAudit.planSubmissionSourceCodeStateAction",
        averageDuration: {
          messageId: "{value}minutes",
          values: { value: 30 }
        },
        recommendedJobTitle: "opsDevOpsEngineer"
      },
      {
        action: "technicalAudit.planSubmissionSurveyAction",
        averageDuration: {
          messageId: "{value}minutes",
          values: { value: 30 }
        },
        recommendedJobTitle: "Cto"
      }
    ],
    []
  );

  const columns = useMemo(
    () => [
      {
        id: "action",
        header: <FormattedMessage id="action" />,
        cell: ({ row: { original } }) => <FormattedMessage id={original.action} />
      },
      {
        id: "averageDuration",
        header: <FormattedMessage id="averageDuration" />,
        cell: ({ row: { original } }) => (
          <FormattedMessage id={original.averageDuration.messageId} values={original.averageDuration.values} />
        )
      },
      {
        id: "recommendedJobTitle",
        header: <FormattedMessage id="recommendedJobTitle" />,
        cell: ({ row: { original } }) => <FormattedMessage id={original.recommendedJobTitle} />
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
          <FormattedMessage
            id="technicalAudit.planSubmissionDetails"
            values={{
              // TODO: probably need to remove p from app.json and component from here
              p: (chunks) => <p>{chunks}</p>
            }}
          />
        </Typography>
      </Grid>
    </Grid>
  );
};

export default PlanSubmission;
