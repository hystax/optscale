import { getSearchParams } from "utils/network";
import { FIELD_NAMES, MAX_RAM, MIN_RAM, MAX_CPU, MIN_CPU, REGIONS } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ currency }: { currency: string }): FormValues => {
  const queryParams = getSearchParams();

  const getCloudTypeValue = () => {
    const value = queryParams[FIELD_NAMES.CLOUD_PROVIDER];

    if (value === undefined) {
      return [];
    }

    return Array.isArray(value) ? value : [value];
  };

  return {
    [FIELD_NAMES.CLOUD_PROVIDER]: getCloudTypeValue(),
    [FIELD_NAMES.REGION]: queryParams[FIELD_NAMES.REGION] ?? REGIONS.EU,
    [FIELD_NAMES.CURRENCY_CODE]: queryParams[FIELD_NAMES.CURRENCY_CODE] ?? currency,
    [FIELD_NAMES.MIN_CPU]: queryParams[FIELD_NAMES.MIN_CPU] ?? MIN_CPU,
    [FIELD_NAMES.MAX_CPU]: queryParams[FIELD_NAMES.MAX_CPU] ?? MAX_CPU,
    [FIELD_NAMES.MIN_RAM]: queryParams[FIELD_NAMES.MIN_RAM] ?? MIN_RAM,
    [FIELD_NAMES.MAX_RAM]: queryParams[FIELD_NAMES.MAX_RAM] ?? MAX_RAM,
  };
};
