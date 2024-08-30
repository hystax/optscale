import CustomTagField, {
  KEY_FIELD_NAME as CUSTOM_TAG_KEY_NAME,
  VALUE_FIELD_NAME as CUSTOM_TAG_VALUE_NAME
} from "./CustomTagField";
import DataSourcesField, { FIELD_NAME as DATA_SOURCES_FIELD_NAME } from "./DataSourcesField";
import FormButtons from "./FormButtons";
import HyperparametersFieldArray, {
  ARRAY_FIELD_NAME as HYPERPARAMETERS_ARRAY_FIELD_NAME,
  NAME_FIELD_NAME as HYPERPARAMETER_NAME_FIELD_NAME,
  ENVIRONMENT_VARIABLE_FIELD as HYPERPARAMETER_ENVIRONMENT_VARIABLE_FIELD_NAME
} from "./HyperparametersFieldArray";
import InstanceTypesField, { FIELD_NAME as INSTANCE_TYPES_FIELD_NAME } from "./InstanceTypesField";
import MaximumParallelRunsField from "./MaximumParallelRunsField";

import MaximumRunsetBudgetField, { FIELD_NAME as MAXIMUM_RUNSET_BUDGET_FIELD_NAME } from "./MaximumRunsetBudgetField";
import NameField, { FIELD_NAME as NAME_FIELD_NAME } from "./NameField";
import PrefixField, { FIELD_NAME as RESOURCE_NAME_PREFIX_NAME } from "./PrefixField";
import RegionsField, { FIELD_NAME as REGIONS_FIELD_NAME } from "./RegionsField";
import TasksField, { FIELD_NAME as TASK_FIELD_NAME } from "./TasksField";

const FIELD_NAMES = Object.freeze({
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
});

export {
  FormButtons,
  CustomTagField,
  MaximumRunsetBudgetField,
  MaximumParallelRunsField,
  NameField,
  PrefixField,
  HyperparametersFieldArray,
  TasksField,
  DataSourcesField,
  RegionsField,
  InstanceTypesField,
  FIELD_NAMES
};
