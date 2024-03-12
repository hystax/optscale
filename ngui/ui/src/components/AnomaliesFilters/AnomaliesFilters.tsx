import ExpandableList from "components/ExpandableList";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";

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
        <KeyValueLabel key={`${name}-${value}`} keyText={displayedName} value={displayedValue} />
      )}
      maxRows={showAll ? appliedItems.length : 5}
    />
  );
};

export default AnomaliesFilters;
