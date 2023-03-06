import React, { Fragment } from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import { Grid, Stack, Typography } from "@mui/material";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import CloudLabel from "components/CloudLabel";
import ExecutorLabel from "components/ExecutorLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LastApplicationRunGoals from "components/LastApplicationRunGoals";
import MlApplicationStatusLabel from "components/MlApplicationStatusLabel";
import MlRunDuration from "components/MlRunDuration";
import SummaryGrid from "components/SummaryGrid";
import SummaryList from "components/SummaryList";
import MlModelRecommendationsContainer from "containers/MlModelRecommendationsContainer";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getEditMlUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  ML_APPLICATION_STATUS,
  ML_MODEL_DETAILS_TABS,
  SUMMARY_CARD_TYPES,
  SUMMARY_VALUE_COMPONENT_TYPES
} from "utils/constants";
import { getTimeDistance } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";

const recommendationMockData = {
  total_savings: 8479.26,
  count: 19
};

const SummaryCards = ({ status, lastRunDuration, totalCost, isLoading }) => {
  const { isDemo } = useOrganizationInfo();

  const items = [
    {
      key: "status",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: MlApplicationStatusLabel,
      valueComponentProps: { status },
      color: {
        [ML_APPLICATION_STATUS.CREATED]: "info",
        [ML_APPLICATION_STATUS.RUNNING]: "primary",
        [ML_APPLICATION_STATUS.COMPLETED]: "success",
        [ML_APPLICATION_STATUS.FAILED]: "error"
      }[status],
      captionMessageId: "status",
      renderCondition: () => status !== undefined,
      isLoading,
      dataTestIds: {
        cardTestId: "card_run_status"
      }
    },
    {
      key: "duration",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: MlRunDuration,
      valueComponentProps: {
        durationInSeconds: lastRunDuration
      },
      renderCondition: () => lastRunDuration && lastRunDuration !== 0,
      captionMessageId: "lastRunDuration",
      dataTestIds: {
        cardTestId: "card_last_run_duration"
      },
      isLoading
    },
    {
      key: "lifetimeCost",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "lifetimeCost",
      isLoading
    },
    // TODO ML: Get real data from "recommendations" api
    {
      key: "totalExpensesMonthToDate",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: recommendationMockData.total_savings
      },
      captionMessageId: "summarySavings",
      relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
      relativeValueComponentProps: {
        value: recommendationMockData.count
      },
      relativeValueCaptionMessageId: "recommendationsCount",
      dataTestIds: {
        cardTestId: "card_total_exp"
      },
      backdrop: {
        show: !isDemo,
        message: <FormattedMessage id="comingSoon" />
      },
      color: recommendationMockData.total_savings || recommendationMockData.count > 20 ? "error" : "success",
      isLoading
    }
  ];

  return <SummaryGrid summaryData={items} />;
};

const LastRunExecutorSummary = ({ isLoading, lastRunExecutor }) => {
  const { isDemo } = useOrganizationInfo();

  const {
    instance_region: instanceRegion,
    instance_id: instanceId,
    instance_type: instanceType,
    platform_type: platformType,
    resource,
    discovered
  } = lastRunExecutor ?? {};

  return (
    <SummaryList
      titleMessage={<FormattedMessage id="lastRunExecutor" />}
      isLoading={isLoading}
      items={[
        lastRunExecutor && (
          <ExecutorLabel
            key="executor_label"
            discovered={discovered}
            resource={resource}
            instanceId={instanceId}
            platformType={platformType}
          />
        ),
        <KeyValueLabel
          key="cloud"
          messageId="cloud"
          value={
            resource && resource.cloud_account ? (
              <CloudLabel
                disableLink={isDemo}
                id={resource.cloud_account.id}
                name={resource.cloud_account.name}
                type={resource.cloud_account.type}
              />
            ) : undefined
          }
        />,
        <KeyValueLabel key="name" messageId="name" value={resource?.name} />,
        <KeyValueLabel key="region" messageId="region" value={instanceRegion} />,
        <KeyValueLabel key="size" messageId="size" value={instanceType} />
      ]}
    />
  );
};

const SummaryInfo = ({
  applicationId,
  applicationGoals,
  lastRunGoals,
  runsCount,
  isLoading,
  lastRunTimestamp,
  lastRunCost,
  ownerName,
  onTabChange,
  lastRunExecutor
}) => (
  <Grid container spacing={SPACING_2}>
    <Grid item xs={12} sm={4}>
      <SummaryList
        titleMessage={<FormattedMessage id="trackedParameters" />}
        titleIconButton={{
          icon: <SettingsIcon fontSize="small" />,
          link: getEditMlUrl(applicationId, { tab: "parameters" })
        }}
        isLoading={isLoading}
        items={
          isEmptyArray(applicationGoals) ? (
            <FormattedMessage id="thereAreNoParameterDefinedForAnApplication" />
          ) : (
            <LastApplicationRunGoals applicationGoals={applicationGoals} lastRunGoals={lastRunGoals} withHistory />
          )
        }
      />
    </Grid>
    <Grid item xs={12} sm={4}>
      <SummaryList
        titleMessage={<FormattedMessage id="applicationSummary" />}
        isLoading={isLoading}
        items={[
          <KeyValueLabel
            key="runs"
            messageId="runs"
            value={
              <>
                <FormattedNumber value={runsCount} />
                &nbsp;
                <FormattedMessage
                  id="linkedText"
                  values={{
                    text: <FormattedMessage id="seeRuns" />,
                    link: (chunks) => (
                      <Link
                        sx={{
                          "&:hover": {
                            textDecoration: "underline",
                            cursor: "pointer"
                          }
                        }}
                        onClick={() => onTabChange(ML_MODEL_DETAILS_TABS.RUNS)}
                      >
                        {chunks}
                      </Link>
                    )
                  }}
                />
              </>
            }
          />,
          <KeyValueLabel
            key="lastSuccessfulRun"
            messageId="lastSuccessfulRun"
            value={
              <FormattedMessage
                id={lastRunTimestamp === 0 ? "never" : "valueAgo"}
                values={{
                  value: lastRunTimestamp ? getTimeDistance(lastRunTimestamp) : null
                }}
              />
            }
          />,
          <KeyValueLabel key="lastRunCost" messageId="lastRunCost" value={<FormattedMoney value={lastRunCost} />} />,
          <KeyValueLabel key="owner" messageId="owner" value={ownerName} />
        ]}
      />
    </Grid>
    <Grid item xs={12} sm={4}>
      <LastRunExecutorSummary isLoading={isLoading} lastRunExecutor={lastRunExecutor} />
    </Grid>
  </Grid>
);

const ModelDetailsSummary = ({ application, isLoading, onTabChange }) => {
  const {
    id: applicationId,
    status,
    last_run_duration: lastRunDuration,
    last_run_cost: lastRunCost = 0,
    run_goals: lastRunGoals = [],
    owner: { name: ownerName } = {},
    last_run: lastRunTimestamp,
    total_cost: totalCost = 0,
    runs_count: runsCount = 0,
    last_run_executor: lastRunExecutor,
    goals: applicationGoals = []
  } = application;

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <SummaryCards status={status} lastRunDuration={lastRunDuration} totalCost={totalCost} isLoading={isLoading} />
      </div>
      <div>
        <SummaryInfo
          applicationId={applicationId}
          applicationGoals={applicationGoals}
          lastRunGoals={lastRunGoals}
          runsCount={runsCount}
          isLoading={isLoading}
          lastRunTimestamp={lastRunTimestamp}
          lastRunCost={lastRunCost}
          ownerName={ownerName}
          onTabChange={onTabChange}
          lastRunExecutor={lastRunExecutor}
        />
      </div>
      <div>
        <Typography component="div" variant="h6">
          <FormattedMessage id="recommendations" />
        </Typography>
        <MlModelRecommendationsContainer />
      </div>
    </Stack>
  );
};

ModelDetailsSummary.propTypes = {
  application: PropTypes.object,
  isLoading: PropTypes.bool,
  onTabChange: PropTypes.func
};

export default ModelDetailsSummary;
