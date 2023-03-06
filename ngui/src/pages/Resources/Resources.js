import React from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import Mocked from "components/Mocked";
import { ResourcesMocked } from "components/Resources";
import ResourcesContainer from "containers/ResourcesContainer";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import {
  DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  getResourcesExpensesUrl,
  GROUP_BY_PARAM_NAME,
  GROUP_TYPE_PARAM_NAME,
  RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME,
  RESOURCES_PERSPECTIVE_PARAMETER_NAME,
  RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME
} from "urls";
import { CLEAN_EXPENSES_BREAKDOWN_TYPES } from "utils/constants";
import { formQueryString } from "utils/network";

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

      const perspectiveSearchParams = {
        ...perspectiveFilters.appliedFilters,
        ...(breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES
          ? {
              [DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME]: breakdownData.breakdownBy,
              [GROUP_BY_PARAM_NAME]: breakdownData.groupBy?.groupBy,
              [GROUP_TYPE_PARAM_NAME]: breakdownData.groupBy?.groupType
            }
          : {}),
        ...(breakdownBy === CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT
          ? {
              [DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME]: breakdownData.breakdownBy
            }
          : {}),
        [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: breakdownBy
      };

      const toSearchParams = formQueryString({
        ...restParams,
        ...perspectiveSearchParams,
        [RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME]: perspective
      });

      return (
        <Navigate
          to={getResourcesExpensesUrl({
            computedParams: toSearchParams
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
