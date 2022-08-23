import React from "react";
import PropTypes from "prop-types";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import KeyValueLabel from "components/KeyValueLabel";

const AnomaliesFilters = ({ filters }) => {
  const filtersInstance = new Filters({
    filters: RESOURCE_FILTERS,
    filterValues: filters
  });

  return filtersInstance.filters.flatMap((filter) =>
    filter.filterValues.map((item) => {
      const appliedItem = filter.getAppliedFilterItem(filter.constructor.getValue(item), item);

      return (
        <KeyValueLabel
          key={appliedItem.appliedValue}
          text={filter.constructor.displayedName}
          value={appliedItem.displayedValue}
        />
      );
    })
  );
};

AnomaliesFilters.propTypes = {
  filters: PropTypes.object.isRequired
};

export default AnomaliesFilters;
