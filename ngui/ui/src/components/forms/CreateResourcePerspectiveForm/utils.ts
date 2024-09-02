import { FIELD_NAMES } from "./constants";

export const getDefaultValues = ({ filters, breakdownBy, breakdownData }) => ({
  [FIELD_NAMES.NAME]: "",
  [FIELD_NAMES.PAYLOAD]: {
    filters,
    breakdownBy,
    breakdownData
  }
});
