import { FormattedMessage } from "react-intl";
import Filters from "components/Filters";
import { ML_RUNS_FILTERS } from "components/Filters/constants";
import LinearSelector from "components/LinearSelector";
import TypographyLoader from "components/TypographyLoader";

const RunsFilter = ({ filterValues, appliedFilters, onChange: onChangeHandler, isLoading }) => {
  const mlRunsFilters = new Filters({
    filters: ML_RUNS_FILTERS,
    filterValues,
    appliedFilters
  });

  const onChange = ({ name, value }) => {
    onChangeHandler((currentlyAppliedFilters) => ({ ...currentlyAppliedFilters, [name]: value }));
  };

  const onFilterDelete = (filterToDelete) => {
    onChangeHandler((currentlyAppliedFilters) => ({ ...currentlyAppliedFilters, [filterToDelete.filterName]: undefined }));
  };

  const onFiltersDelete = () => {
    onChangeHandler((currentlyAppliedFilters) =>
      Object.entries(currentlyAppliedFilters).reduce(
        (newRequestParams, [filterName]) => ({
          ...newRequestParams,
          [filterName]: undefined
        }),
        {}
      )
    );
  };

  return isLoading ? (
    <TypographyLoader linesCount={1} />
  ) : (
    <LinearSelector
      label={<FormattedMessage id="filters" />}
      value={mlRunsFilters.getAppliedValues()}
      items={mlRunsFilters.getFilterSelectors()}
      onClear={onFilterDelete}
      onChange={onChange}
      onClearAll={onFiltersDelete}
    />
  );
};

export default RunsFilter;
