import { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import MlRunsetTemplateForm from "components/MlRunsetTemplateForm";
import { FIELD_NAMES } from "components/MlRunsetTemplateForm/FormElements";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_RUNSET_TEMPLATES, getMlRunsetTemplateUrl } from "urls";
import { RUNSET_TEMPLATE_INSTANCE_TYPES, RUNSET_TEMPLATE_REGIONS } from "utils/constants";

const {
  TASK_FIELD_NAME,
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

const MlRunsetTemplateEdit = ({ runsetTemplate, tasks, dataSources, onSubmit, onCancel, isLoading = {} }) => {
  const {
    isUpdateMlRunsetTemplateLoading = false,
    isGetAllTasksLoading = false,
    isGetRunsetTemplateLoading = false
  } = isLoading;

  const defaultValues = useMemo(() => {
    const {
      name,
      budget,
      name_prefix: resourceNamePrefix,
      tags = {},
      hyperparameters = {},
      cloud_accounts: runsetTemplateDataSources = [],
      tasks: runsetTemplateTasks = [],
      instance_types: runsetTemplateInstanceTypes = [],
      regions: runsetTemplateRegions = []
    } = runsetTemplate;

    const [tagKey, tagName] = Object.entries(tags)[0] ?? [];

    return {
      [NAME_FIELD_NAME]: name,
      [MAXIMUM_RUNSET_BUDGET_FIELD_NAME]: budget,
      [RESOURCE_NAME_PREFIX_NAME]: resourceNamePrefix,
      [CUSTOM_TAG_KEY_NAME]: tagKey,
      [CUSTOM_TAG_VALUE_NAME]: tagName,
      [HYPERPARAMETERS_ARRAY_FIELD_NAME]: Object.entries(hyperparameters).map(
        ([hyperparameterName, hyperparameterEnvironmentVariable]) => ({
          [HYPERPARAMETER_NAME_FIELD_NAME]: hyperparameterName,
          [HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME]: hyperparameterEnvironmentVariable
        })
      ),
      [TASK_FIELD_NAME]: runsetTemplateTasks.filter(
        (runsetTemplateTask) => tasks.find((knownTask) => knownTask.id === runsetTemplateTask.id) !== undefined
      ),
      [DATA_SOURCES_FIELD_NAME]: runsetTemplateDataSources.filter(
        (runsetTemplateDataSource) =>
          dataSources.find((knownDataSource) => knownDataSource.id === runsetTemplateDataSource.id) !== undefined
      ),
      [REGIONS_FIELD_NAME]: RUNSET_TEMPLATE_REGIONS.filter(
        (region) => runsetTemplateRegions.find((runsetTemplateRegion) => runsetTemplateRegion.id === region.id) !== undefined
      ),
      [INSTANCE_TYPES_FIELD_NAME]: RUNSET_TEMPLATE_INSTANCE_TYPES.filter(
        (instanceType) =>
          runsetTemplateInstanceTypes.find(
            (runsetTemplateInstanceType) => runsetTemplateInstanceType.name === instanceType.name
          ) !== undefined
      )
    };
  }, [tasks, dataSources, runsetTemplate]);

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_RUNSET_TEMPLATES} component={RouterLink}>
        <FormattedMessage id="runsetTemplatesTitle" />
      </Link>,
      <Link key={2} to={getMlRunsetTemplateUrl(runsetTemplate.id)} component={RouterLink}>
        {runsetTemplate.name}
      </Link>
    ],
    title: {
      messageId: "editRunsetTemplateTitle",
      isLoading: isGetRunsetTemplateLoading,
      dataTestId: "lbl_edit_runset_template"
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <MlRunsetTemplateForm
            tasks={tasks}
            dataSources={dataSources}
            isLoading={{
              isGetRunsetTemplateLoading,
              isGetAllTasksLoading,
              isSubmitLoading: isUpdateMlRunsetTemplateLoading
            }}
            onSubmit={onSubmit}
            onCancel={onCancel}
            defaultValues={defaultValues}
            isEdit
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default MlRunsetTemplateEdit;
