import { FormControl, Grid } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import Button from "components/Button";
import { SPACING_1 } from "utils/layouts";
import {
  CloudProviderField,
  CurrencyCodeField,
  RegionField,
  MinCpuField,
  MaxCpuField,
  MinRamField,
  MaxRamField
} from "./FormElements";

const CloudCostComparisonFiltersForm = ({ defaultValues, onSubmit }) => {
  const methods = useForm({
    defaultValues
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
            <Button type="submit" messageId="filter" color="primary" />
          </FormControl>
        </div>
      </form>
    </FormProvider>
  );
};

export default CloudCostComparisonFiltersForm;
