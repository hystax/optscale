import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.TASKS]: {
    id: string;
    name: string;
  }[];
  [FIELD_NAMES.DATA_SOURCES]: {
    id: string;
    name: string;
  }[];
  [FIELD_NAMES.REGIONS]: {
    id: string;
    name: string;
    cloudType: string;
  }[];
  [FIELD_NAMES.INSTANCE_TYPES]: {
    id: string;
    name: string;
    cloudType: string;
  }[];
  [FIELD_NAMES.BUDGET]: string;
  [FIELD_NAMES.RESOURCE_NAME_PREFIX]: string;
  [FIELD_NAMES.TAG_KEY]: string;
  [FIELD_NAMES.TAG_VALUE]: string;
  [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.FIELD_NAME]: {
    [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.HYPERPARAMETER_NAME]: string;
    [FIELD_NAMES.HYPERPARAMETERS_FIELD_ARRAY.ENVIRONMENT_VARIABLE]: string;
  }[];
};
