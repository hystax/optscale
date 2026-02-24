import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getHyperparameterFieldName = (environmentVariableName: string) =>
  `${FIELD_NAMES.HYPERPARAMETERS}.${environmentVariableName}` as const;

export const getDefaultValues = (): FormValues => ({
  [FIELD_NAMES.TASK]: "",
  [FIELD_NAMES.DATA_SOURCE]: "",
  [FIELD_NAMES.REGION]: "",
  [FIELD_NAMES.INSTANCE_TYPE]: "",
  [FIELD_NAMES.IMAGE]: "",
  [FIELD_NAMES.VIRTUAL_ENVIRONMENT_PATH]: "",
  [FIELD_NAMES.HYPERPARAMETERS]: {},
  [FIELD_NAMES.CODE_TO_EXECUTE]: "",
  [FIELD_NAMES.MAX_BUDGET_CHECKBOX]: false,
  [FIELD_NAMES.MAX_BUDGET_VALUE]: "",
  [FIELD_NAMES.REACHED_GOALS_CHECKBOX]: false,
  [FIELD_NAMES.MAX_DURATION_CHECKBOX]: false,
  [FIELD_NAMES.MAX_DURATION_VALUE]: "",
  [FIELD_NAMES.USE_SPOT_INSTANCES]: false,
  [FIELD_NAMES.MAX_SPOT_ATTEMPTS]: "1",
  [FIELD_NAMES.MAX_SPOT_COST_PER_HOUR]: "",
});
