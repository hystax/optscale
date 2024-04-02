import { FormattedMessage } from "react-intl";
import Filters from "components/Filters";
import { ML_TASKS_FILTERS } from "components/Filters/constants";
import LinearSelector from "components/LinearSelector";

const MlTasksFilters = ({ appliedFilters, filterValues, onChange: onChangeHandler }) => {
  const mlTasksFilters = new Filters({
    filters: ML_TASKS_FILTERS,
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

  return (
    <LinearSelector
      label={<FormattedMessage id="filters" />}
      value={mlTasksFilters.getAppliedValues()}
      items={mlTasksFilters.getFilterSelectors()}
      onClear={onFilterDelete}
      onChange={onChange}
      onClearAll={onFiltersDelete}
    />
  );
};

export default MlTasksFilters;
