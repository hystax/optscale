import { useMemo } from "react";
import { FormControl } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import LinearSelector from "components/LinearSelector";
import TypographyLoader from "components/TypographyLoader";
import { useResourceFilters } from "hooks/useResourceFilters";
import AvailableFiltersService from "services/AvailableFiltersService";
import { getPoolIdWithSubPools } from "urls";
import { POOL_ID_FILTER } from "utils/constants";
import { getLast30DaysRange } from "utils/datetime";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.FILTERS;

const FiltersView = ({ filters }) => {
  const { control, watch } = useFormContext();

  const appliedFilters = watch(FIELD_NAME);

  const resourceFilters = useResourceFilters(filters, appliedFilters);

  return (
    <FormControl>
      <Controller
        name={FIELD_NAME}
        dataTestId={`selector_${FIELD_NAME}`}
        control={control}
        render={({ field: { onChange, value: formFilterValue } }) => (
          // TODO: Unify with ExpensesFilters
          <LinearSelector
            label={<FormattedMessage id="filters" />}
            value={resourceFilters.getAppliedValues()}
            items={resourceFilters.getFilterSelectors()}
            onChange={({ name: filterName, value, checked }) => {
              if ([POOL_ID_FILTER].includes(filterName)) {
                onChange({
                  ...formFilterValue,
                  [filterName]: checked ? getPoolIdWithSubPools(value) : value
                });
              } else {
                onChange({
                  ...formFilterValue,
                  [filterName]: value
                });
              }
            }}
            onApply={({ name: filterName, value }) => {
              onChange({
                ...formFilterValue,
                [filterName]: value
              });
            }}
            onClear={({ filterName, filterValue }) => {
              const filterValues = formFilterValue[filterName];

              const newFilterValues = [filterValues].flat().filter((value) => value !== filterValue);

              onChange({
                ...formFilterValue,
                [filterName]: newFilterValues
              });
            }}
            onClearAll={() => {
              onChange({});
            }}
          />
        )}
      />
    </FormControl>
  );
};

export const filtersRangeFunction = getLast30DaysRange;

const FiltersContainer = ({ exceptions }) => {
  const { useGet } = AvailableFiltersService();

  const params = useMemo(() => {
    const { startDate, endDate } = filtersRangeFunction();

    return {
      startDate,
      endDate
    };
  }, []);

  const { isLoading, filters } = useGet(params, exceptions);

  return (
    <FormControl fullWidth>{isLoading ? <TypographyLoader linesCount={1} /> : <FiltersView filters={filters} />}</FormControl>
  );
};

const Filters = ({ exceptions }) => <FiltersContainer exceptions={exceptions} />;

export default Filters;
