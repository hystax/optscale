import PoolsRequiringAttentionCard from "components/PoolsRequiringAttentionCard";
import PoolsService from "services/PoolsService";
import { isEmpty } from "utils/arrays";
import { isCostOverLimit, isForecastOverLimit } from "utils/pools";

// TODO: move to generic types when created
type Pool = {
  id: string;
  name: string;
  purpose: string;
  cost: number;
  forecast: number;
  limit: number;
  children?: Pool[];
  hasLimit?: boolean;
  remain?: number;
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
  const withExceededLimit: Pool[] = [];
  const withForecastedOverspend: Pool[] = [];

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

  [...children, rootPool].forEach(({ id, name, purpose, limit = 0, cost = 0, forecast = 0 }) => {
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

    // Pools can technically go into both categories simultaneously, but the goal is to focus on
    if (isCostOverLimit({ limit, cost })) {
      withExceededLimit.push(pool);
    } else if (isForecastOverLimit({ limit, forecast })) {
      withForecastedOverspend.push(pool);
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
