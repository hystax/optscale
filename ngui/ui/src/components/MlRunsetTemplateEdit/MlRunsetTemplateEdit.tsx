import { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import MlRunsetTemplateForm from "components/forms/MlRunsetTemplateForm";
import { FIELD_NAMES } from "components/forms/MlRunsetTemplateForm/constants";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_RUNSET_TEMPLATES, getMlRunsetTemplateUrl } from "urls";
import { RUNSET_TEMPLATE_INSTANCE_TYPES, RUNSET_TEMPLATE_REGIONS } from "utils/constants";

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
      [FIELD_NAMES.NAME]: name,
      [FIELD_NAMES.BUDGET]: budget,
      [FIELD_NAMES.RESOURCE_NAME_PREFIX]: resourceNamePrefix,
      [FIELD_NAMES.TAG_KEY]: tagKey,
      [FIELD_NAMES.TAG_VALUE]: tagName,
      [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.FIELD_NAME]: Object.entries(hyperparameters).map(
        ([hyperparameterName, hyperparameterEnvironmentVariable]) => ({
          [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.HYPERPARAMETER_NAME]: hyperparameterName,
          [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.ENVIRONMENT_VARIABLE]: hyperparameterEnvironmentVariable
        })
      ),
      [FIELD_NAMES.TASKS]: runsetTemplateTasks.filter(
        (runsetTemplateTask) => tasks.find((knownTask) => knownTask.id === runsetTemplateTask.id) !== undefined
      ),
      [FIELD_NAMES.DATA_SOURCES]: runsetTemplateDataSources.filter(
        (runsetTemplateDataSource) =>
          dataSources.find((knownDataSource) => knownDataSource.id === runsetTemplateDataSource.id) !== undefined
      ),
      [FIELD_NAMES.REGIONS]: RUNSET_TEMPLATE_REGIONS.filter(
        (region) => runsetTemplateRegions.find((runsetTemplateRegion) => runsetTemplateRegion.id === region.id) !== undefined
      ),
      [FIELD_NAMES.INSTANCE_TYPES]: RUNSET_TEMPLATE_INSTANCE_TYPES.filter(
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
