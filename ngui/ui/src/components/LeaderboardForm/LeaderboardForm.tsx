import { useEffect } from "react";
import { FormControl, FormLabel, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import HtmlSymbol from "components/HtmlSymbol";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { FIELD_NAMES } from "./constants";
import {
  RunTagsField,
  GroupByHyperparametersSwitch,
  PrimaryMetricSelector,
  SecondaryMetricsSelector,
  MetricRestrictionsFieldArray,
  FormButtons,
  DatasetLabelsCoverageField,
  NameField,
  SelectedDatasets,
  DatasetNavigator
} from "./FormElements";
import { FormValues } from "./types";

const LeaderboardForm = ({
  defaultValues,
  onSubmit,
  onCancel,
  datasets,
  groupingTags,
  metrics,
  datasetLabels,
  isTemplate = false,
  isLoadingProps = {}
}) => {
  const { isGetDataLoading = false, isSubmitDataLoading = false } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset, groupingTags]);

  return (
    <FormProvider {...methods}>
      {isTemplate && <InlineSeverityAlert messageId="leaderboardTemplateDescription" sx={{ mb: 1, width: "100%" }} />}
      <form
        onSubmit={handleSubmit((formData) => {
          const submitData = {
            name: formData[FIELD_NAMES.NAME],
            datasetIds: formData[FIELD_NAMES.SELECTED_DATASETS]?.map(({ id }) => id),
            filters: formData[FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.NAME].map(
              ({
                [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC]: id,
                [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MAX]: max,
                [FIELD_NAMES.METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.METRIC_MIN]: min
              }) => ({
                id,
                max: max ? Number(max) : undefined,
                min: min ? Number(min) : undefined
              })
            ),
            groupByHyperparameters: formData[FIELD_NAMES.GROUP_BY_HYPERPARAMETERS_FIELD_NAME],
            groupingTags: formData[FIELD_NAMES.RUN_TAGS_FIELD_NAME],
            otherMetrics: formData[FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME].map(({ id }) => id),
            primaryMetric: (formData[FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME] as { id: string }).id,
            datasetCoverageRules: Object.fromEntries(
              formData[FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.NAME].map(
                ({
                  [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.DATASET_LABEL]: datasetLabel,
                  [FIELD_NAMES.DATASETS_COVERAGE_ARRAY_FIELD_NAMES.ARRAY_FIELD_NAMES.LAST_DATASETS_COVERED]: lastDataCovered
                }) => [datasetLabel, Number(lastDataCovered)]
              )
            )
          };

          return onSubmit(submitData);
        })}
        noValidate
      >
        {!isTemplate && <NameField isLoading={isGetDataLoading} />}
        <RunTagsField groupingTags={groupingTags} isLoading={isGetDataLoading} />
        <GroupByHyperparametersSwitch isLoading={isGetDataLoading} />
        <PrimaryMetricSelector metrics={metrics} isLoading={isGetDataLoading} />
        <SecondaryMetricsSelector metrics={metrics} isLoading={isGetDataLoading} />
        <FormLabel component="p">
          <FormattedMessage id="qualificationProtocol" />
        </FormLabel>
        <FormControl>
          <Typography>
            <FormattedMessage id="candidateMustFollowMetricRestrictions" />
            <HtmlSymbol symbol="colon" />
          </Typography>
        </FormControl>
        <MetricRestrictionsFieldArray metrics={metrics} isLoading={isGetDataLoading} />
        <FormLabel component="p">
          <FormattedMessage id="datasetsCoverageRules" />
        </FormLabel>
        <FormControl>
          <Typography>
            <FormattedMessage id="candidateMustCoverDatasetsWithLabels" />
            <HtmlSymbol symbol="colon" />
          </Typography>
        </FormControl>
        <DatasetLabelsCoverageField labels={datasetLabels} isLoading={isGetDataLoading} />
        {!isTemplate && (
          <>
            <FormControl>
              <Typography>
                <FormattedMessage id="candidateMustCoverFollowingDatasets" />
                <HtmlSymbol symbol="colon" />
              </Typography>
            </FormControl>
            <FormControl fullWidth>
              <SelectedDatasets isLoading={isGetDataLoading} />
            </FormControl>
            <FormControl fullWidth margin="normal">
              <DatasetNavigator datasets={datasets} isLoading={isGetDataLoading} />
            </FormControl>
          </>
        )}
        <FormButtons isLoading={isGetDataLoading || isSubmitDataLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default LeaderboardForm;
