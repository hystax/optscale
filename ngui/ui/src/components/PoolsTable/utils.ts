import { isEmpty as isEmptyArray } from "utils/arrays";
import { isEmpty as isEmptyObject } from "utils/objects";
import { getRemain, getHasLimit } from "utils/pools";

export const patchPools = (rootPool) => {
  if (isEmptyObject(rootPool)) {
    return {};
  }

  const childrenUpdated =
    rootPool.children?.map((pool) => {
      const patchedPool = {
        ...pool,
        hasChildren: rootPool.children.some(({ parent_id: parentId }) => parentId === pool.id),
        hasLimit: getHasLimit(pool),
        remain: getRemain(pool)
      };

      return patchedPool;
    }) ?? [];

  const rootPoolPatched = {
    ...rootPool,
    hasChildren: !isEmptyArray(rootPool.children ?? []),
    hasLimit: getHasLimit(rootPool),
    remain: getRemain(rootPool)
  };

  return {
    ...rootPoolPatched,
    children: childrenUpdated
  };
};
