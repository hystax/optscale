import { isEmpty as isEmptyArray } from "utils/arrays";
import { isEmpty as isEmptyObject } from "utils/objects";

export const isCostOverLimit = ({ limit, cost }) => limit > 0 && limit < cost;

export const isForecastOverLimit = ({ limit, forecast }) => limit > 0 && limit < forecast;

const getRemain = (pool) => pool.limit - pool.cost;
const getHasLimit = (pool) => pool.limit !== 0;

const getSelfAssignedItem = (item, allPools, selfAssignedName) => {
  const { children, expenses_export_link: _, policies, unallocated_limit: unallocatedLimit, id, ...itemInfo } = item;

  const { cost: selfCost, forecast: selfForecast } = allPools.reduce(
    (acc, { cost, forecast, parent_id: parentId }) => {
      if (id === parentId) {
        return { cost: acc.cost - cost, forecast: acc.forecast - forecast };
      }

      return acc;
    },
    { cost: item.cost, forecast: item.forecast }
  );

  return {
    ...itemInfo,
    parent_id: item.id,
    name: selfAssignedName,
    purpose: undefined,
    cost: selfCost,
    forecast: selfForecast,
    limit: unallocatedLimit
  };
};

export const patchPools = (rootPool, selfAssignedNameFn) => {
  if (isEmptyObject(rootPool)) {
    return {};
  }

  const selfAssignedChildren = [];

  const childrenUpdated = rootPool.children?.map((pool) => {
    const patchedPool = {
      ...pool,
      hasChildren: rootPool.children.some(({ parent_id: parentId }) => parentId === pool.id),
      hasLimit: getHasLimit(pool),
      remain: getRemain(pool)
    };

    if (patchedPool.hasChildren) {
      selfAssignedChildren.push(getSelfAssignedItem(patchedPool, rootPool.children, selfAssignedNameFn(patchedPool.name)));
    }

    return patchedPool;
  });

  const rootPoolPatched = {
    ...rootPool,
    hasChildren: !isEmptyArray(rootPool.children ?? []),
    hasLimit: getHasLimit(rootPool),
    remain: getRemain(rootPool)
  };

  // also adding self assigned pool for root pool
  if (rootPoolPatched.hasChildren) {
    selfAssignedChildren.push(
      getSelfAssignedItem(rootPoolPatched, rootPool.children, selfAssignedNameFn(rootPoolPatched.name))
    );
  }

  return {
    ...rootPoolPatched,
    children: [...childrenUpdated, ...selfAssignedChildren]
  };
};
