import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { RESOURCE_FILTERS_NAMES } from "components/Filters/constants";
import Resources from "components/Resources";
import { useDefaultDateRange } from "hooks/useDefaultDateRange";
import AvailableFiltersService from "services/AvailableFiltersService";
import { DATE_RANGE_TYPE, START_DATE_FILTER, END_DATE_FILTER, EXPENSES_LIMIT_FILTER_DEFAULT_VALUE } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

const getRequestParams = (startDateTimestamp, endDateTimestamp) => {
  const queryParams = getQueryParams();

  const getFiltersRequestParams = () =>
    RESOURCE_FILTERS_NAMES.reduce(
      (params, queryKey) => ({
        ...params,
        [queryKey]: queryParams[queryKey]
      }),
      {}
    );

  return {
    limit: Number(queryParams.limit || EXPENSES_LIMIT_FILTER_DEFAULT_VALUE),
    [START_DATE_FILTER]: startDateTimestamp,
    [END_DATE_FILTER]: endDateTimestamp,
    ...getFiltersRequestParams()
  };
};

const ResourcesContainer = ({ fromMainMenu }) => {
  const { useGet: useGetFilters } = AvailableFiltersService();

  const [startDateTimestamp, endDateTimestamp] = useDefaultDateRange(DATE_RANGE_TYPE.RESOURCES);

  const [requestParams, setRequestParams] = useState(() => getRequestParams(startDateTimestamp, endDateTimestamp));

  const { isLoading: isFilterValuesLoading, filters: filterValues } = useGetFilters(requestParams);

  useEffect(() => {
    updateQueryParams(requestParams);
  }, [requestParams]);

  const onApply = (data) => setRequestParams((params) => ({ ...params, ...data }));

  const onFilterAdd = (newFilter) => setRequestParams((params) => ({ ...params, ...newFilter }));

  const onFilterDelete = (filtersToDelete) => {
    setRequestParams((currentState) => {
      let stateCopy = currentState;
      Object.entries(filtersToDelete).forEach(([key, valueToDelete]) => {
        const { [key]: currentValue } = stateCopy;

        const newValue = Array.isArray(currentValue) ? currentValue.filter((val) => val !== valueToDelete) : undefined;

        stateCopy = { ...stateCopy, [key]: newValue };
      });
      return stateCopy;
    });
  };

  const onFiltersDelete = () => {
    setRequestParams((prevRequestParams) =>
      Object.entries(prevRequestParams).reduce(
        (newRequestParams, [filterName, filterValue]) =>
          RESOURCE_FILTERS_NAMES.includes(filterName)
            ? {
                ...newRequestParams,
                [filterName]: undefined
              }
            : {
                ...newRequestParams,
                [filterName]: filterValue
              },
        []
      )
    );
  };

  return (
    <Resources
      startDateTimestamp={startDateTimestamp}
      endDateTimestamp={endDateTimestamp}
      filters={requestParams}
      filterValues={filterValues}
      onApply={onApply}
      onFilterAdd={onFilterAdd}
      onFilterDelete={onFilterDelete}
      onFiltersDelete={onFiltersDelete}
      fromMainMenu={fromMainMenu}
      requestParams={requestParams}
      isFilterValuesLoading={isFilterValuesLoading}
    />
  );
};

ResourcesContainer.propTypes = {
  fromMainMenu: PropTypes.bool.isRequired
};

export default ResourcesContainer;
