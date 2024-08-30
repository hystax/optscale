import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.POOL_ID]: string;
  [FIELD_NAMES.INCLUDE_CHILDREN]: boolean;
};
