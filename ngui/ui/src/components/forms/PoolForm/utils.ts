import { POOL_TYPE_BUDGET } from "utils/constants";
import { FIELD_NAMES } from "./constants";
import { CreatePoolFormValues, EditPoolFormValues } from "./types";

export const getEditFormDefaultValues = ({
  poolName,
  limitAmount,
  defaultResourceOwnerId,
  type
}: {
  poolName: string;
  limitAmount: number;
  defaultResourceOwnerId: string;
  type: string;
}): EditPoolFormValues => ({
  [FIELD_NAMES.NAME]: poolName,
  [FIELD_NAMES.LIMIT]: String(limitAmount),
  [FIELD_NAMES.TYPE]: type,
  [FIELD_NAMES.OWNER]: defaultResourceOwnerId,
  [FIELD_NAMES.AUTO_EXTENSION]: false
});

export const getCreateFormDefaultValues = (): CreatePoolFormValues => ({
  [FIELD_NAMES.NAME]: "",
  [FIELD_NAMES.LIMIT]: "",
  [FIELD_NAMES.TYPE]: POOL_TYPE_BUDGET,
  [FIELD_NAMES.AUTO_EXTENSION]: false
});
