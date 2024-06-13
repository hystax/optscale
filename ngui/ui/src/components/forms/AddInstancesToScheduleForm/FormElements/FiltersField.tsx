import { FormControl } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import ExpensesFilters from "components/ExpensesFilters";
import Filters from "components/Filters";
import { POWER_SCHEDULE_INSTANCES_FILTERS } from "components/Filters/constants";
import TypographyLoader from "components/TypographyLoader";
import { FormValues } from "../types";
import { FIELD_NAME as INSTANCES_FIELD_NAME } from "./InstancesField";

export const FIELD_NAME = "filters";

const FiltersField = ({ filterValues, isLoading }) => {
  const { control, resetField, watch } = useFormContext<FormValues>();

  const appliedFilters = watch(FIELD_NAME);

  const resourceFilters = new Filters({
    filters: POWER_SCHEDULE_INSTANCES_FILTERS,
    filterValues,
    appliedFilters
  });

  const items = resourceFilters.getFilterSelectors();
  const appliedValues = resourceFilters.getAppliedValues();

  return (
    <FormControl fullWidth>
      <Controller
        name={FIELD_NAME}
        control={control}
        render={({ field: { onChange, value } }) =>
          isLoading ? (
            <TypographyLoader linesCount={1} />
          ) : (
            <ExpensesFilters
              items={items}
              appliedValues={appliedValues}
              onFilterAdd={(newFilter) => {
                onChange({ ...value, ...newFilter });
                resetField(INSTANCES_FIELD_NAME);
              }}
              onFilterDelete={(filterName, filterValue) => {
                const { [filterName]: filterToDeleteValues, ...rest } = value;

                onChange({
                  ...rest,
                  [filterName]: Array.isArray(filterToDeleteValues)
                    ? filterToDeleteValues.filter((val) => val !== filterValue)
                    : undefined
                });
                resetField(INSTANCES_FIELD_NAME);
              }}
              onFiltersDelete={() => {
                onChange({});
                resetField(INSTANCES_FIELD_NAME);
              }}
            />
          )
        }
      />
    </FormControl>
  );
};

export default FiltersField;
