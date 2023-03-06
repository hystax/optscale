import React from "react";
import PropTypes from "prop-types";
import MlExecutorsBreakdown from "components/MlExecutorsBreakdown";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";
import { getExecutorsBreakdown } from "utils/mlDemoData/utils";

const DemoBreakdown = ({ breakdownBy, getFilteredBreakdown }) => (
  <MlExecutorsBreakdown
    breakdown={getFilteredBreakdown(getExecutorsBreakdown(breakdownBy))}
    breakdownBy={breakdownBy}
    isLoading={false}
  />
);

const Breakdown = ({ getFilteredBreakdown, breakdownBy }) => {
  const { useGetBreakdown } = MlExecutorsService();

  const { breakdown, isLoading } = useGetBreakdown({ breakdownBy });

  return <MlExecutorsBreakdown breakdown={getFilteredBreakdown(breakdown)} breakdownBy={breakdownBy} isLoading={isLoading} />;
};

const MlExecutorsBreakdownContainer = ({ dateRange, breakdownBy = ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU }) => {
  const { isDemo } = useOrganizationInfo();

  const getFilteredBreakdown = (breakdown) =>
    Object.fromEntries(
      Object.entries(breakdown).filter(([secondsTimestamp]) => inDateRange(dateRange, secondsToMilliseconds(secondsTimestamp)))
    );

  return isDemo ? (
    <DemoBreakdown breakdownBy={breakdownBy} getFilteredBreakdown={getFilteredBreakdown} />
  ) : (
    <Breakdown breakdownBy={breakdownBy} getFilteredBreakdown={getFilteredBreakdown} />
  );
};

MlExecutorsBreakdownContainer.propTypes = {
  breakdownBy: PropTypes.oneOf(Object.values(ML_EXECUTORS_DAILY_BREAKDOWN_BY)),
  dateRange: PropTypes.object
};

export default MlExecutorsBreakdownContainer;
