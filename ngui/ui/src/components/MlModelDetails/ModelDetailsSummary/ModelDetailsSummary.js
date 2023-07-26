import React from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import { Box, Stack } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import CloudLabel from "components/CloudLabel";
import ExecutorLabel from "components/ExecutorLabel";
import FormattedDuration from "components/FormattedDuration";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LastModelRunGoals from "components/LastModelRunGoals";
import MlModelRecommendations from "components/MlModelRecommendations";
import MlModelStatus from "components/MlModelStatus";
import SubTitle from "components/SubTitle";
import SummaryGrid from "components/SummaryGrid";
import SummaryList from "components/SummaryList";
import MlModelRunsListContainer from "containers/MlModelRunsListContainer";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getEditMlModelUrl } from "urls";
import { ML_MODEL_STATUS, SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { getTimeDistance } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

const SummaryCards = ({ status, lastRunDuration, recommendationsCount, totalSaving, totalCost, isModelDetailsLoading }) => {
  const items = [
    {
      key: "status",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: MlModelStatus,
      valueComponentProps: { status, iconSize: "medium" },
      color: {
        [ML_MODEL_STATUS.CREATED]: "info",
        [ML_MODEL_STATUS.RUNNING]: "primary",
        [ML_MODEL_STATUS.ABORTED]: "info",
        [ML_MODEL_STATUS.COMPLETED]: "success",
        [ML_MODEL_STATUS.FAILED]: "error"
      }[status],
      captionMessageId: "status",
      renderCondition: () => status !== undefined,
      isLoading: isModelDetailsLoading,
      dataTestIds: {
        cardTestId: "card_run_status"
      }
    },
    {
      key: "duration",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: FormattedDuration,
      valueComponentProps: {
        durationInSeconds: lastRunDuration
      },
      renderCondition: () => lastRunDuration && lastRunDuration !== 0,
      captionMessageId: "lastRunDuration",
      dataTestIds: {
        cardTestId: "card_last_run_duration"
      },
      isLoading: isModelDetailsLoading
    },
    {
      key: "lifetimeCost",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "lifetimeCost",
      isLoading: isModelDetailsLoading
    },
    {
      key: "recommendations",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
      },
      captionMessageId: "summarySavings",
      relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
      relativeValueComponentProps: {
        value: recommendationsCount
      },
      relativeValueCaptionMessageId: "recommendationsCount",
      dataTestIds: {
        cardTestId: "card_total_exp"
      },
      color: totalSaving || recommendationsCount > 20 ? "error" : "success",
      isLoading: isModelDetailsLoading
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
  modelId,
  modelKey,
  lastRunReachedGoals,
  lastRunGoals,
  runsCount,
  isLoading,
  lastSuccessfulRunTimestamp,
  lastRunCost,
  ownerName,
  lastRunExecutor
}) => (
  <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
    <Box>
      <SummaryList
        titleMessage={<FormattedMessage id="trackedParameters" />}
        titleIconButton={{
          icon: <SettingsIcon fontSize="small" />,
          link: getEditMlModelUrl(modelId, { tab: "parameters" })
        }}
        isLoading={isLoading}
        items={
          isEmptyObject(lastRunReachedGoals) ? (
            <FormattedMessage id="thereAreNoParameterDefinedForModel" />
          ) : (
            <LastModelRunGoals lastRunGoals={lastRunGoals} modelReachedGoals={lastRunReachedGoals} />
          )
        }
      />
    </Box>
    <Box>
      <SummaryList
        titleMessage={<FormattedMessage id="modelSummary" />}
        isLoading={isLoading}
        items={[
          <KeyValueLabel key="key" messageId="key" value={modelKey} />,
          <KeyValueLabel key="runs" messageId="runs" value={<FormattedNumber value={runsCount} />} />,
          <KeyValueLabel
            key="lastSuccessfulRun"
            messageId="lastSuccessfulRun"
            value={
              <FormattedMessage
                id={lastSuccessfulRunTimestamp === 0 ? "never" : "valueAgo"}
                values={{
                  value: lastSuccessfulRunTimestamp ? getTimeDistance(lastSuccessfulRunTimestamp) : null
                }}
              />
            }
          />,
          <KeyValueLabel key="lastRunCost" messageId="lastRunCost" value={<FormattedMoney value={lastRunCost} />} />,
          <KeyValueLabel key="owner" messageId="owner" value={ownerName} />
        ]}
      />
    </Box>
    <Box>
      <LastRunExecutorSummary isLoading={isLoading} lastRunExecutor={lastRunExecutor} />
    </Box>
  </Box>
);

const ModelDetailsSummary = ({
  model,
  recommendations,
  isModelDetailsLoading = false,
  isGetRecommendationsLoading = false
}) => {
  const {
    id: modelId,
    key: modelKey,
    status,
    last_run_duration: lastRunDuration,
    last_run_cost: lastRunCost = 0,
    run_goals: lastRunGoals = [],
    owner: { name: ownerName } = {},
    last_successful_run: lastSuccessfulRunTimestamp,
    total_cost: totalCost = 0,
    runs_count: runsCount = 0,
    last_run_executor: lastRunExecutor,
    last_run_reached_goals: lastRunReachedGoals = {}
  } = model;

  const { total_count: recommendationsCount, total_saving: totalSaving } = recommendations;

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <SummaryCards
          status={status}
          recommendationsCount={recommendationsCount}
          totalSaving={totalSaving}
          lastRunDuration={lastRunDuration}
          totalCost={totalCost}
          isModelDetailsLoading={isModelDetailsLoading}
        />
      </div>
      <div>
        <SummaryInfo
          modelId={modelId}
          modelKey={modelKey}
          lastRunReachedGoals={lastRunReachedGoals}
          lastRunGoals={lastRunGoals}
          runsCount={runsCount}
          isLoading={isModelDetailsLoading}
          lastSuccessfulRunTimestamp={lastSuccessfulRunTimestamp}
          lastRunCost={lastRunCost}
          ownerName={ownerName}
          lastRunExecutor={lastRunExecutor}
        />
      </div>
      <div>
        <SubTitle>
          <FormattedMessage id="recommendations" />
        </SubTitle>
        <MlModelRecommendations modelId={modelId} isLoading={isGetRecommendationsLoading} recommendations={recommendations} />
      </div>
      <div>
        <SubTitle>
          <FormattedMessage id="runs" />
        </SubTitle>
        <MlModelRunsListContainer />
      </div>
    </Stack>
  );
};

ModelDetailsSummary.propTypes = {
  recommendations: PropTypes.shape({
    total_saving: PropTypes.number.isRequired,
    total_count: PropTypes.number.isRequired,
    optimizations: PropTypes.object.isRequired
  }),
  model: PropTypes.object,
  isModelDetailsLoading: PropTypes.bool,
  isGetRecommendationsLoading: PropTypes.bool,
  onTabChange: PropTypes.func
};

export default ModelDetailsSummary;
