import { FIELD_NAMES } from "./constants";

export const getDefaultValues = ({ email }: { email?: string }) => ({
  [FIELD_NAMES.EMAIL]: email ?? "",
  [FIELD_NAMES.PASSWORD]: ""
});
