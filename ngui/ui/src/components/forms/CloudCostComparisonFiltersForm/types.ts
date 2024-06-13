import { currencyCodes } from "utils/currency";
import { ArrayValues, ObjectValues } from "utils/types";
import { FIELD_NAMES, REGIONS } from "./constants";

type Region = ObjectValues<typeof REGIONS>;

type Currency = ArrayValues<typeof currencyCodes>;

export type FormValues = {
  [FIELD_NAMES.CLOUD_PROVIDER]: string[];
  [FIELD_NAMES.REGION]: Region;
  [FIELD_NAMES.CURRENCY_CODE]: Currency;
  [FIELD_NAMES.MIN_CPU]: string;
  [FIELD_NAMES.MAX_CPU]: string;
  [FIELD_NAMES.MIN_RAM]: string;
  [FIELD_NAMES.MAX_RAM]: string;
};

export type CloudCostComparisonFiltersFormProps = {
  defaultValues: FormValues;
  onSubmit: (formData: FormValues) => void;
};
