import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.DATA_SOURCES]: string[];
  [FIELD_NAMES.FILTERS]: {
    ownerId?: string;
    poolId?: string;
    region?: string;
    tag?: string;
  };
  [FIELD_NAMES.INSTANCES]: Record<string, boolean>;
};
