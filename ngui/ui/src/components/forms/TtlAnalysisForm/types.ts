import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.POOL_ID]: string;
  [FIELD_NAMES.TTL_MODE]: string;
  [FIELD_NAMES.CUSTOM_TTL]: string;
  [FIELD_NAMES.START_DATE_PICKER_NAME]: number;
  [FIELD_NAMES.END_DATE_PICKER_NAME]: number;
};
