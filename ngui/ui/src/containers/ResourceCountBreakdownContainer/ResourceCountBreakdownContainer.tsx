import ResourceCountBreakdown from "components/ResourceCountBreakdown";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import ResourcesCountBreakdownService from "services/ResourcesCountBreakdownService";
import { DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME } from "urls";

const getCountKeysSortedByAverageInDescendingOrder = (counts) =>
  Object.entries(counts)
    .sort(([, { average: averageA }], [, { average: averageB }]) => averageB - averageA)
    .map(([name]) => name);

const ResourceCountBreakdownContainer = ({ requestParams }) => {
  const { useGet } = ResourcesCountBreakdownService();

  const [{ value: breakdownByValue }, onBreakdownByChange] = useBreakdownBy({
    queryParamName: DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME
  });

  const {
    isGetResourceCountBreakdownLoading,
    data: { breakdown = {}, counts = {} }
  } = useGet(breakdownByValue, requestParams);

  const countKeysSortedByTotalInDescendingOrder = getCountKeysSortedByAverageInDescendingOrder(counts);

  return (
    <ResourceCountBreakdown
      breakdown={breakdown}
      breakdownByValue={breakdownByValue}
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

export default ResourceCountBreakdownContainer;
