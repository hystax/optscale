import PoolsRequiringAttentionCard from "components/PoolsRequiringAttentionCard";
import { isCostOverLimit, isForecastOverLimit } from "components/PoolsTable/utils";
import PoolsService from "services/PoolsService";
import { isEmpty } from "utils/arrays";

// TODO: move to generic types when created
type Pool = {
  id: string;
  name: string;
  purpose: string;
  cost: number;
  forecast: number;
  limit: number;
  children: Pool[];
};

const hasLimit = (limit: number) => limit !== 0;
const getRemain = (limit: number, cost: number) => limit - cost;

const getRequiringAttentionPools = ({
  id: rootId,
  name: rootName,
  purpose: rootPurpose,
  cost: rootCost = 0,
  forecast: rootForecast = 0,
  limit: rootLimit = 0,
  children = []
}: Pool) => {
  const withExceededLimit = [];
  const withForecastedOverspend = [];

  // Calculate for children pools
  children.forEach(({ id, name, purpose, limit = 0, cost = 0, forecast = 0 }) => {
    const withLimit = hasLimit(limit);
    const remain = getRemain(limit, cost);
    const pool = {
      id,
      name,
      purpose,
      cost,
      forecast,
      hasLimit: withLimit,
      remain,
      limit
    };

    // Pools can go into both categories simultaneously
    if (isCostOverLimit({ limit, cost })) {
      withExceededLimit.push(pool);
    }
    if (isForecastOverLimit({ limit, forecast })) {
      withForecastedOverspend.push(pool);
    }
  });

  // Calculate for root/parent pool
  const withRootLimit = hasLimit(rootLimit);
  const rootRemain = getRemain(rootLimit, rootCost);

  const rootPool = {
    id: rootId,
    name: rootName,
    purpose: rootPurpose,
    cost: rootCost,
    forecast: rootForecast,
    hasLimit: withRootLimit,
    remain: rootRemain,
    limit: rootLimit
  };

  if (isCostOverLimit({ limit: rootLimit, cost: rootCost })) {
    withExceededLimit.push(rootPool);
  }
  if (isForecastOverLimit({ limit: rootLimit, forecast: rootForecast })) {
    withForecastedOverspend.push(rootPool);
  }

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
