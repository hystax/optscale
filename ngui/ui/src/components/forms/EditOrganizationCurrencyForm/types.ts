import { currencyCodes } from "utils/currency";
import { ArrayValues } from "utils/types";
import { FIELD_NAMES } from "./constants";

export type Currency = ArrayValues<typeof currencyCodes>;

export type FormValues = {
  [FIELD_NAMES.CURRENCY]: Currency;
};

export type EditOrganizationCurrencyFormProps = {
  defaultCurrency: Currency;
  onSubmit: (formData: FormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
};
