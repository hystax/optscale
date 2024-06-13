import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
  [FIELD_NAMES.SAVE_AS]: string;
  [FIELD_NAMES.SHARE]: boolean;
};
