import React from "react";
import { useParams } from "react-router-dom";
import ExecutionBreakdown, { ExecutionBreakdownLoader } from "components/ExecutionBreakdown";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getRunBreakdown } from "utils/mlDemoData/utils";
import { isEmpty as isEmptyObject } from "utils/objects";

const getData = ({ breakdown = {}, milestones = [], stages = [] }) => {
  if (isEmptyObject(breakdown)) {
    return {
      breakdown: {},
      milestones: [],
      stages: []
    };
  }

  const breakdownEntries = Object.entries(breakdown);

  const firstTimestamp = breakdownEntries[0][0];
  const timestampToSeconds = (timestamp) => timestamp - firstTimestamp;

  return {
    breakdown: Object.fromEntries(
      Object.entries(breakdown)
        .filter(([, { data = {}, metrics = {} }]) => !isEmptyObject(data) || !isEmptyObject(metrics))
        .map(([timestamp, data]) => [timestampToSeconds(timestamp), data])
    ),
    milestones: milestones.map((milestone) => {
      const { timestamp } = milestone;
      return {
        ...milestone,
        time: timestampToSeconds(timestamp)
      };
    }),
    stages: stages.map((stage) => {
      const { start, end } = stage;

      return {
        ...stage,
        startTimestamp: start,
        endTimestamp: end,
        start: timestampToSeconds(start),
        end: end ? timestampToSeconds(end) : null
      };
    })
  };
};

const DemoContainer = ({ reachedGoals }) => {
  const { runId } = useParams();

  return <ExecutionBreakdown {...getData(getRunBreakdown(runId))} reachedGoals={reachedGoals} />;
};

const Container = ({ reachedGoals }) => {
  const { useGetRunBreakdown } = MlModelsService();

  const { runId } = useParams();

  const { isLoading, isDataReady, breakdown = {}, milestones = [], stages = [] } = useGetRunBreakdown(runId);

  return isLoading || !isDataReady ? (
    <ExecutionBreakdownLoader />
  ) : (
    <ExecutionBreakdown {...getData({ breakdown, milestones, stages })} reachedGoals={reachedGoals} />
  );
};

const ExecutionBreakdownContainer = ({ reachedGoals }) => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer reachedGoals={reachedGoals} /> : <Container reachedGoals={reachedGoals} />;
};

export default ExecutionBreakdownContainer;
