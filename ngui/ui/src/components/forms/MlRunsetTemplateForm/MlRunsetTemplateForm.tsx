import { useEffect } from "react";
import FormLabel from "@mui/material/FormLabel";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { OPTSCALE_MODE } from "utils/constants";
import { FIELD_NAMES } from "./constants";
import {
  FormButtons,
  CustomTagField,
  MaximumRunsetBudgetField,
  MaximumParallelRunsField,
  NameField,
  PrefixField,
  HyperparametersFieldArray,
  DataSourcesField,
  RegionsField,
  InstanceTypesField,
  TasksField
} from "./FormElements";
import { FormValues } from "./types";

const UNLIMITED_BUDGET = 999999;

const MlRunsetTemplateForm = ({ tasks, dataSources, onSubmit, onCancel, isLoading = {}, defaultValues, isEdit }) => {
  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const { isGetAllTasksLoading = false, isGetRunsetTemplateLoading = false, isSubmitLoading = false } = isLoading;

  const methods = useForm<FormValues>({
    defaultValues
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    // TODO ML EK: Merge with form values
    reset(defaultValues);
  }, [defaultValues, reset]);

  return (
    <FormProvider {...methods}>
      <InlineSeverityAlert
        messageId="runsetTemplateDescription"
        sx={{
          width: "100%"
        }}
      />
      <form
        data-test-id="runset_template_form"
        onSubmit={handleSubmit((formData) => {
          const data = {
            name: formData[FIELD_NAMES.NAME],
            task_ids: formData[FIELD_NAMES.TASKS].map(({ id }) => id),
            cloud_account_ids: formData[FIELD_NAMES.DATA_SOURCES].map(({ id }) => id),
            region_ids: formData[FIELD_NAMES.REGIONS].map(({ id }) => id),
            instance_types: formData[FIELD_NAMES.INSTANCE_TYPES].map(({ name }) => name),
            budget: isFinOpsEnabled ? Number(formData[FIELD_NAMES.BUDGET]) : UNLIMITED_BUDGET,
            name_prefix: formData[FIELD_NAMES.RESOURCE_NAME_PREFIX],
            tags: {
              [formData[FIELD_NAMES.TAG_KEY]]: formData[FIELD_NAMES.TAG_VALUE]
            },
            hyperparameters: Object.fromEntries(
              formData[FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.FIELD_NAME].map((field) => {
                const hyperparameterName = field[FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.HYPERPARAMETER_NAME];
                const hyperparameterEnvironmentVariable = field[FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.ENVIRONMENT_VARIABLE];

                return [hyperparameterName, hyperparameterEnvironmentVariable];
              })
            )
          };

          onSubmit(data);
        })}
        noValidate
      >
        <FormLabel component="p">
          <FormattedMessage id="templateInformation" />
        </FormLabel>
        <NameField isLoading={isGetRunsetTemplateLoading} />
        <TasksField tasks={tasks} isLoading={isGetAllTasksLoading || isGetRunsetTemplateLoading} />
        <FormLabel component="p">
          <FormattedMessage id="runsetSettings" />
        </FormLabel>
        <DataSourcesField dataSources={dataSources} isLoading={isGetRunsetTemplateLoading} />
        <RegionsField isLoading={isGetRunsetTemplateLoading} />
        <InstanceTypesField isLoading={isGetRunsetTemplateLoading} />
        <MaximumParallelRunsField />
        {isFinOpsEnabled && <MaximumRunsetBudgetField isLoading={isGetRunsetTemplateLoading} />}
        <PrefixField isLoading={isGetRunsetTemplateLoading} />
        <CustomTagField isLoading={isGetRunsetTemplateLoading} />
        <HyperparametersFieldArray isLoading={isGetRunsetTemplateLoading} />
        <FormButtons
          onCancel={onCancel}
          isEdit={isEdit}
          isLoading={isGetRunsetTemplateLoading || isGetAllTasksLoading || isSubmitLoading}
        />
      </form>
    </FormProvider>
  );
};

export default MlRunsetTemplateForm;
