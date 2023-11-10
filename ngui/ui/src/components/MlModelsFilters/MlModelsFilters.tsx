import { FormattedMessage } from "react-intl";
import Filters from "components/Filters";
import { ML_MODELS_FILTERS } from "components/Filters/constants";
import LinearSelector from "components/LinearSelector";

const MlModelsFilters = ({ appliedFilters, filterValues, onChange: onChangeHandler }) => {
  const mlModelsFilters = new Filters({
    filters: ML_MODELS_FILTERS,
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
      value={mlModelsFilters.getAppliedValues()}
      items={mlModelsFilters.getFilterSelectors()}
      onClear={onFilterDelete}
      onChange={onChange}
      onClearAll={onFiltersDelete}
    />
  );
};

export default MlModelsFilters;
