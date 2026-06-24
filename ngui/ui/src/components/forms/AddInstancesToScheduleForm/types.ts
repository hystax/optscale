import { FIELD_NAMES } from "./constants";

export type TagEntry = { key: string; value: string };

export type FormValues = {
  [FIELD_NAMES.DATA_SOURCES]: string[];
  [FIELD_NAMES.FILTERS]: {
    ownerId?: string;
    poolId?: string;
    region?: string;
    tag?: string;
  };
  [FIELD_NAMES.INSTANCES]: Record<string, boolean>;
  [FIELD_NAMES.TAG_INCLUDE_EC2]: boolean;
  [FIELD_NAMES.TAG_INCLUDE_RDS]: boolean;
  [FIELD_NAMES.TAG_ENTRIES]: TagEntry[];
};
