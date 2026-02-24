import { useMemo } from "react";
import { FormLabel } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import ResourceFilters from "components/Resources/Filters";
import TypographyLoader from "components/TypographyLoader";
import AvailableFiltersService from "services/AvailableFiltersService";
import { getLast30DaysRange } from "utils/datetime";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.FILTERS;

const FiltersView = ({ filterValues }) => {
  const { control } = useFormContext();

  return (
    <>
      <FormLabel component="p">
        <FormattedMessage id="filters" />
      </FormLabel>
      <Controller
        name={FIELD_NAME}
        control={control}
        render={({ field: { onChange, value: appliedFilters } }) => (
          <ResourceFilters
            filters={filterValues}
            appliedFilters={appliedFilters}
            onAppliedFiltersChange={(newFilters) => {
              onChange({
                ...appliedFilters,
                ...newFilters,
              });
            }}
          />
        )}
      />
    </>
  );
};

export const filtersRangeFunction = getLast30DaysRange;

const FiltersContainer = ({ exceptions }) => {
  const { useGet } = AvailableFiltersService();

  const params = useMemo(() => {
    const { startDate, endDate } = filtersRangeFunction();

    return {
      startDate,
      endDate,
    };
  }, []);

  const { isLoading, filters: filterValues } = useGet(params, exceptions);

  return isLoading ? <TypographyLoader linesCount={1} /> : <FiltersView filterValues={filterValues} />;
};

const Filters = ({ exceptions }) => <FiltersContainer exceptions={exceptions} />;

export default Filters;
