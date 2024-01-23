import PoolsRequiringAttentionCard from "components/PoolsRequiringAttentionCard";
import { isCostOverLimit, isForecastOverLimit } from "components/PoolsTable/utils";
import PoolsService from "services/PoolsService";
import { isEmpty } from "utils/arrays";

const getRequiringAttentionPools = ({
  id: rootId,
  name: rootName,
  purpose: rootPurpose,
  cost: rootCost = 0,
  forecast: rootForecast = 0,
  limit: rootLimit = 0,
  children = []
}) => {
  // Make a flat list of child pools and neccessary root pool fields
  const allPools = [
    ...children,
    {
      id: rootId,
      name: rootName,
      cost: rootCost,
      forecast: rootForecast,
      purpose: rootPurpose,
      parent_id: null,
      limit: rootLimit
    }
  ];

  const withExceededLimit = [];
  const withForecastedOverspend = [];

  allPools.forEach(({ id, name, purpose, limit = 0, cost = 0, forecast = 0 }) => {
    // To get actual pool data, find all children and and substract cost, forecast and limit from current pool
    const poolChildren = allPools.filter(({ parent_id: parentId }) => id === parentId);

    let poolCost = cost;
    let poolForecast = forecast;
    let poolLimit = limit;

    // Just skipped if there are no children, the origical values are taken
    poolChildren.forEach(({ cost: childCost = 0, forecast: childForecast = 0, limit: childLimit = 0 }) => {
      poolCost -= childCost;
      poolForecast -= childForecast;
      poolLimit -= childLimit;
    });

    // Pools can go into both categories simultaneously
    if (isCostOverLimit({ limit: poolLimit, cost: poolCost })) {
      withExceededLimit.push({ id, name, purpose, cost: poolCost, forecast: poolForecast });
    }
    if (isForecastOverLimit({ limit: poolLimit, forecast: poolForecast })) {
      withForecastedOverspend.push({ id, name, purpose, cost: poolCost, forecast: poolForecast });
    }
  });

  return { withExceededLimit, withForecastedOverspend };
};

const PoolsRequiringAttentionCardContainer = () => {
  const { useGet } = PoolsService();
  const { isLoading, data } = useGet();

  const { withExceededLimit, withForecastedOverspend } = getRequiringAttentionPools(data);

  return (
    <PoolsRequiringAttentionCard
      isLoading={isLoading}
      withExceededLimit={withExceededLimit}
      withForecastedOverspend={withForecastedOverspend}
      rootPoolLimitUnset={data.limit === 0 && data.parent_id === null && isEmpty(data.children)}
    />
  );
};

export default PoolsRequiringAttentionCardContainer;
