import { useEffect, Fragment } from "react";
import FormControl from "@mui/material/FormControl";
import { FormProvider, useForm, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CodeEditor from "components/CodeEditor";
import DashedTypography from "components/DashedTypography";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import MlRunsetTagForCreatedResourcesChip from "components/MlRunsetTagForCreatedResourcesChip";
import QuestionMark from "components/QuestionMark";
import SubTitle from "components/SubTitle";
import TypographyLoader from "components/TypographyLoader";
import { isLastItem } from "utils/arrays";
import { ML_RUNSET_ABORT_CONDITION_TYPES } from "utils/constants";
import { convertMinutesToSeconds, convertSecondsToMinutes } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import {
  AbortConditionsFields,
  TaskField,
  CommandToExecuteField,
  DataSourceField,
  FIELD_NAMES,
  FormButtons,
  HyperparametersField,
  InstanceTypeField,
  MaximumParallelRunsField,
  RegionField,
  SpotInstanceFields
} from "./FormElements";

const {
  TASK_FIELD_NAME,
  DATA_SOURCE_FIELD_NAME,
  REGION_FIELD_NAME,
  INSTANCE_TYPE_FIELD_NAME,
  COMMAND_TO_EXECUTE_FIELD_NAME,
  getHyperparameterFieldName,
  HYPERPARAMETERS_FIELD_NAME,
  ABORT_CONDITION_MAX_BUDGET_CHECKBOX_FIELD_NAME,
  ABORT_CONDITION_MAX_BUDGET_VALUE_FIELD_NAME,
  ABORT_CONDITION_REACHED_GOALS_CHECKBOX_FIELD_NAME,
  ABORT_CONDITION_MAX_DURATION_CHECKBOX_FIELD_NAME,
  ABORT_CONDITION_MAX_DURATION_VALUE_FIELD_NAME,
  SPOT_INSTANCES_USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME,
  SPOT_INSTANCES_MAX_ATTEMPTS_FIELD_NAME
} = FIELD_NAMES;

const FillFromLastRun = ({ latestRunset, hyperparameters, dataSources, tasks, instanceTypes, regions, isLoading }) => {
  const {
    setValue,
    trigger,
    formState: { isSubmitted }
  } = useFormContext();

  if (isLoading) {
    return <TypographyLoader linesCount={1} />;
  }

  if (isEmptyObject(latestRunset)) {
    return null;
  }

  const {
    task: { id: latestRunsetTaskId } = {},
    cloud_account: { id: latestRunsetDataSourceId } = {},
    region: { name: latestRunsetRegionName } = {},
    hyperparameters: latestRunsetHyperparameters = {},
    commands: latestRunsetCodeToExecute,
    destroy_conditions: latestRunsetAbortConditions = {},
    instance_size: { type: latestRunsetInstanceType },
    spot_settings: spotSettings
  } = latestRunset;

  const isKnownTask = () => tasks.find((task) => task.id === latestRunsetTaskId);
  const isKnownDataSource = () => dataSources.find((dataSource) => dataSource.id === latestRunsetDataSourceId);
  const isKnownRegion = () => regions.find((region) => region.name === latestRunsetRegionName);
  const isKnownInstanceType = () => instanceTypes.find((instanceType) => instanceType.name === latestRunsetInstanceType);

  return (
    <DashedTypography
      onClick={() => {
        setValue(TASK_FIELD_NAME, isKnownTask() ? latestRunsetTaskId : "");
        setValue(DATA_SOURCE_FIELD_NAME, isKnownDataSource() ? latestRunsetDataSourceId : "");
        setValue(REGION_FIELD_NAME, isKnownRegion() ? latestRunsetRegionName : "");
        setValue(INSTANCE_TYPE_FIELD_NAME, isKnownInstanceType() ? latestRunsetInstanceType : "");

        if (spotSettings) {
          setValue(SPOT_INSTANCES_USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME, true);
          setValue(SPOT_INSTANCES_MAX_ATTEMPTS_FIELD_NAME, spotSettings.tries);
        }

        Object.values(hyperparameters).forEach((environmentVariableName) => {
          setValue(
            getHyperparameterFieldName(environmentVariableName),
            latestRunsetHyperparameters[environmentVariableName] ?? ""
          );
        });

        setValue(COMMAND_TO_EXECUTE_FIELD_NAME, latestRunsetCodeToExecute);

        setValue(
          ABORT_CONDITION_MAX_BUDGET_CHECKBOX_FIELD_NAME,
          latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.MAX_BUDGET] !== undefined
        );
        setValue(
          ABORT_CONDITION_MAX_BUDGET_VALUE_FIELD_NAME,
          latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.MAX_BUDGET] ?? ""
        );

        setValue(
          ABORT_CONDITION_REACHED_GOALS_CHECKBOX_FIELD_NAME,
          latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.REACHED_GOALS] ?? false
        );

        setValue(
          ABORT_CONDITION_MAX_DURATION_CHECKBOX_FIELD_NAME,
          latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION] !== undefined
        );
        setValue(
          ABORT_CONDITION_MAX_DURATION_VALUE_FIELD_NAME,
          latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION]
            ? convertSecondsToMinutes(latestRunsetAbortConditions[ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION])
            : ""
        );

        if (isSubmitted) {
          trigger();
        }
      }}
      fontWeight="bold"
    >
      <FormattedMessage id="fillFromLatestLaunch" />
    </DashedTypography>
  );
};

const MlRunsetConfigurationForm = ({ runsetTemplate = {}, latestRunset = {}, onSubmit, onCancel, isLoading = false }) => {
  const { isGetRunsetTemplateLoading = false, isGetLatestRunsetLoading = false, isCreateRunsetLoading = false } = isLoading;

  const {
    name_prefix: resourceNamePrefix,
    tags = {},
    hyperparameters = {},
    cloud_accounts: dataSources = [],
    tasks = [],
    instance_types: instanceTypes = [],
    regions = []
  } = runsetTemplate;

  const runsetDataSources = dataSources.filter(({ deleted }) => !deleted);

  const runsetTasks = tasks.filter(({ deleted }) => !deleted);

  const methods = useForm({
    defaultValues: {
      [TASK_FIELD_NAME]: "",
      [DATA_SOURCE_FIELD_NAME]: "",
      [REGION_FIELD_NAME]: "",
      [INSTANCE_TYPE_FIELD_NAME]: "",
      [HYPERPARAMETERS_FIELD_NAME]: {},
      [COMMAND_TO_EXECUTE_FIELD_NAME]: "",
      [ABORT_CONDITION_MAX_BUDGET_CHECKBOX_FIELD_NAME]: false,
      [ABORT_CONDITION_MAX_BUDGET_VALUE_FIELD_NAME]: "",
      [ABORT_CONDITION_REACHED_GOALS_CHECKBOX_FIELD_NAME]: false,
      [ABORT_CONDITION_MAX_DURATION_CHECKBOX_FIELD_NAME]: false,
      [ABORT_CONDITION_MAX_DURATION_VALUE_FIELD_NAME]: "",
      [SPOT_INSTANCES_USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME]: false,
      [SPOT_INSTANCES_MAX_ATTEMPTS_FIELD_NAME]: 1
    }
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      [HYPERPARAMETERS_FIELD_NAME]: Object.fromEntries(
        Object.values(hyperparameters).map((environmentVariableName) => [environmentVariableName, ""])
      )
    }));
  }, [hyperparameters, reset]);

  return (
    <FormProvider {...methods}>
      <form
        noValidate
        onSubmit={handleSubmit((formData) => {
          const getDestroyConditions = () => {
            const conditions = Object.fromEntries(
              [
                {
                  isEnabled: formData[ABORT_CONDITION_MAX_BUDGET_CHECKBOX_FIELD_NAME],
                  name: ML_RUNSET_ABORT_CONDITION_TYPES.MAX_BUDGET,
                  value: Number(formData[ABORT_CONDITION_MAX_BUDGET_VALUE_FIELD_NAME])
                },
                {
                  isEnabled: formData[ABORT_CONDITION_REACHED_GOALS_CHECKBOX_FIELD_NAME],
                  name: ML_RUNSET_ABORT_CONDITION_TYPES.REACHED_GOALS,
                  value: formData[ABORT_CONDITION_REACHED_GOALS_CHECKBOX_FIELD_NAME]
                },
                {
                  isEnabled: formData[ABORT_CONDITION_MAX_DURATION_CHECKBOX_FIELD_NAME],
                  name: ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION,
                  value: convertMinutesToSeconds(Number(formData[ABORT_CONDITION_MAX_DURATION_VALUE_FIELD_NAME]))
                }
              ]
                .filter(({ isEnabled }) => isEnabled)
                .map(({ name: conditionName, value: conditionValue }) => [conditionName, conditionValue])
            );

            return isEmptyObject(conditions) ? undefined : conditions;
          };

          const data = {
            task_id: formData[TASK_FIELD_NAME],
            cloud_account_id: formData[DATA_SOURCE_FIELD_NAME],
            region_id: formData[REGION_FIELD_NAME],
            instance_type: formData[INSTANCE_TYPE_FIELD_NAME],
            name_prefix: resourceNamePrefix,
            commands: formData[COMMAND_TO_EXECUTE_FIELD_NAME],
            tags,
            hyperparameters: formData[HYPERPARAMETERS_FIELD_NAME],
            destroy_conditions: getDestroyConditions(),
            ...(formData[SPOT_INSTANCES_USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME]
              ? { spot_settings: { tries: Number(formData[SPOT_INSTANCES_MAX_ATTEMPTS_FIELD_NAME]) } }
              : {})
          };

          onSubmit(data);
        })}
      >
        <FillFromLastRun
          latestRunset={latestRunset}
          dataSources={runsetDataSources}
          tasks={runsetTasks}
          hyperparameters={hyperparameters}
          instanceTypes={instanceTypes}
          regions={regions}
          isLoading={isGetRunsetTemplateLoading || isGetLatestRunsetLoading}
        />
        <FormControl fullWidth>
          {isGetRunsetTemplateLoading ? (
            <TypographyLoader linesCount={2} />
          ) : (
            <>
              <KeyValueLabel keyMessageId="resourceNamePrefix" value={resourceNamePrefix} />
              <KeyValueLabel
                keyMessageId="tagForCreatedResources"
                value={
                  isEmptyObject(tags)
                    ? undefined
                    : Object.entries(tags).map(([tagKey, tagValue], index, array) => (
                        <Fragment key={tagKey}>
                          <MlRunsetTagForCreatedResourcesChip tagKey={tagKey} tagValue={tagValue} />
                          {isLastItem(index, array.length) ? null : <>&nbsp;</>}
                        </Fragment>
                      ))
                }
              />
            </>
          )}
        </FormControl>
        <TaskField tasks={runsetTasks} isLoading={isGetRunsetTemplateLoading} />
        <DataSourceField dataSources={runsetDataSources} isLoading={isGetRunsetTemplateLoading} />
        <RegionField regions={regions} isLoading={isGetRunsetTemplateLoading} />
        <InstanceTypeField instanceTypes={instanceTypes} isLoading={isGetRunsetTemplateLoading} />
        <SpotInstanceFields />
        <MaximumParallelRunsField />
        <FormControl fullWidth>
          <div style={{ display: "flex", alignItems: "center" }}>
            <SubTitle>
              <FormattedMessage id="hyperparameters" />
            </SubTitle>
            <QuestionMark messageId="hyperparametersTooltip" />
          </div>
          <HyperparametersField hyperparameters={hyperparameters} isLoading={isGetRunsetTemplateLoading} />
        </FormControl>
        <FormControl fullWidth>
          <SubTitle>
            <div style={{ display: "flex", alignItems: "center" }}>
              <SubTitle>
                <FormattedMessage id="commandsToExecute" />
              </SubTitle>
              <QuestionMark
                messageId="commandsToExecuteTooltip"
                messageValues={{
                  br: <br />,
                  example: (
                    <CodeEditor
                      value={"pip install <imports>\nwget <path_to_your_task/task.py>\npython3 task.py"}
                      language="bash"
                    />
                  )
                }}
              />
            </div>
          </SubTitle>
          <CommandToExecuteField />
        </FormControl>
        <FormControl fullWidth>
          <SubTitle>
            <FormattedMessage id="abortConditions" />
          </SubTitle>
          <AbortConditionsFields />
        </FormControl>
        <FormButtons
          onCancel={onCancel}
          isLoading={isGetRunsetTemplateLoading || isGetLatestRunsetLoading || isCreateRunsetLoading}
        />
      </form>
    </FormProvider>
  );
};

export default MlRunsetConfigurationForm;
