import { Navigate, useSearchParams } from "react-router-dom";
import Mocked from "components/Mocked";
import { ResourcesMocked } from "components/Resources";
import ResourcesContainer from "containers/ResourcesContainer";
import { useOrganizationPerspectives } from "hooks/coreData/useOrganizationPerspectives";
import {
  DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_META_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  getResourcesExpensesUrl,
  GROUP_BY_PARAM_NAME,
  GROUP_TYPE_PARAM_NAME,
  isPoolIdWithSubPools,
  RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME,
  RESOURCES_PERSPECTIVE_PARAMETER_NAME,
  RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME,
} from "urls";
import { CLEAN_EXPENSES_BREAKDOWN_TYPES } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import { stringifySearchParams } from "utils/network";

const Resources = () => {
  const [searchParams] = useSearchParams();

  const { [RESOURCES_PERSPECTIVE_PARAMETER_NAME]: perspective, ...restParams } = Object.fromEntries(
    new URLSearchParams(searchParams)
  );

  const { validPerspectives } = useOrganizationPerspectives();

  if (perspective) {
    const selectedPerspective = validPerspectives[perspective];

    if (selectedPerspective) {
      const { filters: perspectiveFilters, breakdownBy, breakdownData } = validPerspectives[perspective];

      const { poolId, firstSeen, lastSeen, ...restFilters } = perspectiveFilters.appliedFilters;

      const getPoolFilters = () => {
        if (poolId.every((pool) => isPoolIdWithSubPools(pool))) {
          return {
            poolId,
          };
        }

        return {
          poolId: poolId.map((pool) => {
            if (isPoolIdWithSubPools(pool)) {
              return pool.slice(0, -1);
            }

            return pool;
          }),
        };
      };

      const perspectiveSearchParams = {
        ...(poolId ? getPoolFilters() : {}),
        ...(firstSeen
          ? {
              firstSeenFrom: firstSeen.from ? millisecondsToSeconds(firstSeen.from) : undefined,
              firstSeenTo: firstSeen.to ? millisecondsToSeconds(firstSeen.to) : undefined,
            }
          : {}),
        ...(lastSeen
          ? {
              lastSeenFrom: lastSeen.from ? millisecondsToSeconds(lastSeen.from) : undefined,
              lastSeenTo: lastSeen.to ? millisecondsToSeconds(lastSeen.to) : undefined,
            }
          : {}),
        ...restFilters,
        ...(breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES
          ? {
              [DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME]: breakdownData.breakdownBy,
              [GROUP_BY_PARAM_NAME]: breakdownData.groupBy?.groupBy,
              [GROUP_TYPE_PARAM_NAME]: breakdownData.groupBy?.groupType,
            }
          : {}),
        ...(breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT
          ? {
              [DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME]: breakdownData.breakdownBy,
            }
          : {}),
        ...(breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.META
          ? {
              [DAILY_META_BREAKDOWN_BY_PARAMETER_NAME]: breakdownData.breakdownBy,
            }
          : {}),
        [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: breakdownBy,
      };

      const toSearchParams = stringifySearchParams({
        ...restParams,
        ...perspectiveSearchParams,
        [RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME]: perspective,
      });

      return (
        <Navigate
          to={getResourcesExpensesUrl({
            computedParams: toSearchParams,
          })}
        />
      );
    }
  }

  return (
    <Mocked mock={<ResourcesMocked />}>
      <ResourcesContainer />
    </Mocked>
  );
};

export default Resources;
