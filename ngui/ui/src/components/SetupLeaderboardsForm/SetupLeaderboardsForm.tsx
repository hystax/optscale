import { useEffect } from "react";
import { FormControl, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { defaultValues as formDefaultValues } from "./constants";
import {
  RunTagsField,
  GroupByHyperparametersSwitch,
  PrimaryMetricSelector,
  SecondaryMetricsSelector,
  MetricRestrictionsField,
  FormButtons
} from "./FormElements";

const SetupLeaderboardsForm = ({
  metrics,
  runTags,
  onSubmit,
  onCancel,
  isLoadingProps = {},
  defaultValues = formDefaultValues
}) => {
  const { isGetDataLoading = false, isSubmitDataLoading = false } = isLoadingProps;

  const methods = useForm({
    defaultValues
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset, runTags]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <RunTagsField runTags={runTags} isLoading={isGetDataLoading} />
        <GroupByHyperparametersSwitch isLoading={isGetDataLoading} />
        <PrimaryMetricSelector metrics={metrics} isLoading={isGetDataLoading} />
        <SecondaryMetricsSelector metrics={metrics} isLoading={isGetDataLoading} />
        <FormControl>
          <Typography>
            <FormattedMessage id="leaderboardQualificationProtocol.metricRestrictions" />
          </Typography>
        </FormControl>
        <MetricRestrictionsField metrics={metrics} isLoading={isGetDataLoading} />
        <FormButtons isLoading={isGetDataLoading || isSubmitDataLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default SetupLeaderboardsForm;
