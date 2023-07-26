import React, { useEffect } from "react";
import FormLabel from "@mui/material/FormLabel";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import {
  FormButtons,
  CustomTagField,
  MaximumRunsetBudgetField,
  MaximumParallelRunsField,
  NameField,
  PrefixField,
  HyperparameterField,
  FIELD_NAMES,
  DataSourcesField,
  RegionsField,
  InstanceTypesField,
  ModelsField
} from "./FormElements";

const {
  MODELS_FIELD_NAME,
  DATA_SOURCES_FIELD_NAME,
  REGIONS_FIELD_NAME,
  INSTANCE_TYPES_FIELD_NAME,
  NAME_FIELD_NAME,
  RESOURCE_NAME_PREFIX_NAME,
  MAXIMUM_RUNSET_BUDGET_FIELD_NAME,
  CUSTOM_TAG_KEY_NAME,
  CUSTOM_TAG_VALUE_NAME,
  HYPERPARAMETERS_ARRAY_FIELD_NAME,
  HYPERPARAMETER_NAME_FIELD_NAME,
  HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME
} = FIELD_NAMES;

const MlRunsetTemplateForm = ({ models, dataSources, onSubmit, onCancel, isLoading = {}, defaultValues, isEdit }) => {
  const { isGetAllModelsLoading = false, isGetRunsetTemplateLoading = false, isSubmitLoading = false } = isLoading;

  const methods = useForm({
    defaultValues
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    // TODO ML EK: Merge with form values
    reset(defaultValues);
  }, [defaultValues, reset]);

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="runset_template_form"
        onSubmit={handleSubmit((formData) => {
          const data = {
            name: formData[NAME_FIELD_NAME],
            application_ids: formData[MODELS_FIELD_NAME].map(({ id }) => id),
            cloud_account_ids: formData[DATA_SOURCES_FIELD_NAME].map(({ id }) => id),
            region_ids: formData[REGIONS_FIELD_NAME].map(({ id }) => id),
            instance_types: formData[INSTANCE_TYPES_FIELD_NAME].map(({ name }) => name),
            budget: Number(formData[MAXIMUM_RUNSET_BUDGET_FIELD_NAME]),
            name_prefix: formData[RESOURCE_NAME_PREFIX_NAME],
            tags: {
              [formData[CUSTOM_TAG_KEY_NAME]]: formData[CUSTOM_TAG_VALUE_NAME]
            },
            hyperparameters: Object.fromEntries(
              formData[HYPERPARAMETERS_ARRAY_FIELD_NAME].map((field) => {
                const hyperparameterName = field[HYPERPARAMETER_NAME_FIELD_NAME];
                const hyperparameterEnvironmentVariable = field[HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME];

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
        <ModelsField models={models} isLoading={isGetAllModelsLoading || isGetRunsetTemplateLoading} />
        <FormLabel component="p">
          <FormattedMessage id="runsetSettings" />
        </FormLabel>
        <DataSourcesField dataSources={dataSources} isLoading={isGetRunsetTemplateLoading} />
        <RegionsField isLoading={isGetRunsetTemplateLoading} />
        <InstanceTypesField isLoading={isGetRunsetTemplateLoading} />
        <MaximumParallelRunsField />
        <MaximumRunsetBudgetField isLoading={isGetRunsetTemplateLoading} />
        <PrefixField isLoading={isGetRunsetTemplateLoading} />
        <CustomTagField isLoading={isGetRunsetTemplateLoading} />
        <HyperparameterField isLoading={isGetRunsetTemplateLoading} />
        <FormButtons
          onCancel={onCancel}
          isEdit={isEdit}
          isLoading={isGetRunsetTemplateLoading || isGetAllModelsLoading || isSubmitLoading}
        />
      </form>
    </FormProvider>
  );
};

MlRunsetTemplateForm.propTypes = {
  models: PropTypes.array.isRequired,
  dataSources: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.shape({
    isGetAllModelsLoading: PropTypes.bool,
    isGetRunsetTemplateLoading: PropTypes.bool,
    isSubmitLoading: PropTypes.bool
  }),
  defaultValues: PropTypes.object,
  isEdit: PropTypes.bool
};

export default MlRunsetTemplateForm;
