import { FIELD_NAMES } from "./constants";
import { Currency } from "./types";

export const getDefaultValues = ({ currency }: { currency: Currency }) => ({
  [FIELD_NAMES.CURRENCY]: currency
});
