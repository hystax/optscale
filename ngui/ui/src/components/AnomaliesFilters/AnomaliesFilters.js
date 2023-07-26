import React from "react";
import PropTypes from "prop-types";
import ExpandableList from "components/ExpandableList";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import KeyValueLabel from "components/KeyValueLabel";

const AnomaliesFilters = ({ filters, showAll = false }) => {
  const filtersInstance = new Filters({
    filters: RESOURCE_FILTERS,
    filterValues: filters
  });

  const appliedItems = filtersInstance.getFilterValuesAsAppliedItems();

  return (
    <ExpandableList
      items={appliedItems}
      render={({ name, value, displayedValue, displayedName }) => (
        <KeyValueLabel key={`${name}-${value}`} text={displayedName} value={displayedValue} />
      )}
      maxRows={showAll ? appliedItems.length : 5}
    />
  );
};

AnomaliesFilters.propTypes = {
  filters: PropTypes.object.isRequired,
  showAll: PropTypes.bool
};

export default AnomaliesFilters;
