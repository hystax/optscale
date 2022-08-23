import React from "react";
import PropTypes from "prop-types";
import ResourceCountBreakdown from "components/ResourceCountBreakdown";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import ResourcesCountBreakdownService from "services/ResourcesCountBreakdownService";

const RESOURCE_COUNT_BREAKDOWN_QUERY_PARAM_NAME = "resourceCountBreakdownBy";

const getCountKeysSortedByAverageInDescendingOrder = (counts) =>
  Object.entries(counts)
    .sort(([, { average: averageA }], [, { average: averageB }]) => averageB - averageA)
    .map(([name]) => name);

const ResourceCountBreakdownContainer = ({ requestParams }) => {
  const { useGet } = ResourcesCountBreakdownService();

  const [breakdownBy, onBreakdownByChange] = useBreakdownBy({ queryParamName: RESOURCE_COUNT_BREAKDOWN_QUERY_PARAM_NAME });

  const {
    isGetResourceCountBreakdownLoading,
    data: { breakdown = {}, counts = {} }
  } = useGet(breakdownBy, requestParams);

  const countKeysSortedByTotalInDescendingOrder = getCountKeysSortedByAverageInDescendingOrder(counts);

  return (
    <ResourceCountBreakdown
      breakdown={breakdown}
      breakdownBy={breakdownBy}
      onBreakdownByChange={onBreakdownByChange}
      counts={counts}
      countKeys={countKeysSortedByTotalInDescendingOrder}
      isLoading={isGetResourceCountBreakdownLoading}
      appliedRange={{
        startSecondsTimestamp: Number(requestParams.startDate),
        endSecondsTimestamp: Number(requestParams.endDate)
      }}
    />
  );
};

ResourceCountBreakdownContainer.propTypes = {
  breakdownBy: PropTypes.string,
  requestParams: PropTypes.object
};

export default ResourceCountBreakdownContainer;
