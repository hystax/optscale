import ExpandableList from "components/ExpandableList";
import { FILTER_TYPE } from "components/FilterComponents/constants";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import { isEmptyArray } from "utils/arrays";

const MAX_ROWS = 5;

const AnomaliesFilters = ({ filters, showAll = false }) => {
  const filterItems = Object.values(FILTER_CONFIGS).flatMap((config) => {
    if (config.type === FILTER_TYPE.SELECTION) {
      const appliedFilters = filters[config.apiName] ?? [];

      if (isEmptyArray(appliedFilters)) {
        return [];
      }

      return appliedFilters.map((appliedFilter) => {
        const value = config.transformers.getValue(appliedFilter);

        return {
          key: `${config.id}-${value}`,
          filterName: config.label,
          filterValue: config.renderPerspectiveItem(value, appliedFilters),
        };
      });
    }

    if (config.type === FILTER_TYPE.RANGE) {
      const from = filters[config.fromApiName];
      const to = filters[config.toApiName];

      if (!from && !to) {
        return [];
      }

      return [
        {
          key: `${config.id}-${from}-${to}`,
          filterName: config.label,
          filterValue: config.renderPerspectiveItem({ from, to }),
        },
      ];
    }

    return [];
  });

  return (
    <ExpandableList
      items={filterItems}
      render={({ key, filterName, filterValue }) => <KeyValueLabel key={key} keyText={filterName} value={filterValue} />}
      maxRows={showAll ? filters.length : MAX_ROWS}
    />
  );
};

export default AnomaliesFilters;
