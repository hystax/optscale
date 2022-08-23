import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import LinearSelector from "components/LinearSelector";
import { useResourceFilters } from "hooks/useResourceFilters";
import { getPoolIdWithSubPools } from "urls";
import { isEmpty } from "utils/arrays";
import { POOL_ID_FILTER } from "utils/constants";

const ExpensesFilters = ({ filterValues, appliedFilters, onFilterAdd, onFilterDelete, onFiltersDelete }) => {
  const resourceFilters = useResourceFilters(filterValues, appliedFilters);

  const items = resourceFilters.getFilterSelectors();

  return (
    !isEmpty(items) && (
      <LinearSelector
        label={<FormattedMessage id="filters" />}
        value={resourceFilters.getAppliedValues()}
        items={items}
        onChange={({ name: filterName, value, checked }) => {
          if ([POOL_ID_FILTER].includes(filterName)) {
            onFilterAdd({
              [filterName]: checked ? getPoolIdWithSubPools(value) : value
            });
          } else {
            onFilterAdd({ [filterName]: value });
          }
        }}
        onApply={({ name, value }) => {
          onFilterAdd({
            [name]: value
          });
        }}
        onClear={({ filterName, filterValue }) => {
          onFilterDelete({ [filterName]: filterValue });
        }}
        onClearAll={onFiltersDelete}
      />
    )
  );
};

ExpensesFilters.propTypes = {
  appliedFilters: PropTypes.object.isRequired,
  filterValues: PropTypes.object.isRequired,
  onFilterAdd: PropTypes.func.isRequired,
  onFilterDelete: PropTypes.func.isRequired,
  onFiltersDelete: PropTypes.func.isRequired
};

export default ExpensesFilters;
