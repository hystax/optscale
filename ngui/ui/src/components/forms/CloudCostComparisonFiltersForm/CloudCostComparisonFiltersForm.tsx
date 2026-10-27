import { FormControl, Grid } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SPACING_1 } from "utils/layouts";
import {
  CloudProviderField,
  CurrencyCodeField,
  RegionField,
  MinCpuField,
  MaxCpuField,
  MinRamField,
  MaxRamField,
} from "./FormElements";
import { CloudCostComparisonFiltersFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CloudCostComparisonFiltersForm = ({ onSubmit, isLoading = false }: CloudCostComparisonFiltersFormProps) => {
  const { currency } = useOrganizationInfo();

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({ currency }),
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Grid container spacing={SPACING_1}>
          <Grid item xs={12} lg={4}>
            <CloudProviderField />
          </Grid>
          <Grid item xs={12} lg={4}>
            <RegionField />
          </Grid>
          <Grid item xs={12} lg={4}>
            <CurrencyCodeField />
          </Grid>
          <Grid item xs={12} lg={3}>
            <MinCpuField />
          </Grid>
          <Grid item xs={12} lg={3}>
            <MaxCpuField />
          </Grid>
          <Grid item xs={12} lg={3}>
            <MinRamField />
          </Grid>
          <Grid item xs={12} lg={3}>
            <MaxRamField />
          </Grid>
        </Grid>
        <div>
          <FormControl>
            <ButtonLoader type="submit" messageId="filter" color="primary" isLoading={isLoading} />
          </FormControl>
        </div>
      </form>
    </FormProvider>
  );
};

export default CloudCostComparisonFiltersForm;
