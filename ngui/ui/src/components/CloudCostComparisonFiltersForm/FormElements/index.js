import CloudProviderField, { FIELD_NAME as CLOUD_TYPE_FIELD_NAME, SUPPORTED_CLOUD_TYPES } from "./CloudProviderField";
import CurrencyCodeField, { FIELD_NAME as CURRENCY_CODE_FIELD_NAME } from "./CurrencyCodeField";
import MaxCpuField, { FIELD_NAME as MAX_CPU_FIELD_NAME } from "./MaxCpuField";
import MaxRamField, { FIELD_NAME as MAX_RAM_FIELD_NAME } from "./MaxRamField";
import MinCpuField, { FIELD_NAME as MIN_CPU_FIELD_NAME } from "./MinCpuField";
import MinRamField, { FIELD_NAME as MIN_RAM_FIELD_NAME } from "./MinRamField";
import RegionField, { FIELD_NAME as REGION_FIELD_NAME } from "./RegionField";

const FIELD_NAMES = Object.freeze({
  REGION_FIELD_NAME,
  CLOUD_TYPE_FIELD_NAME,
  CURRENCY_CODE_FIELD_NAME,
  MIN_CPU_FIELD_NAME,
  MAX_CPU_FIELD_NAME,
  MIN_RAM_FIELD_NAME,
  MAX_RAM_FIELD_NAME
});

export { SUPPORTED_CLOUD_TYPES };
export { RegionField, CloudProviderField, CurrencyCodeField, FIELD_NAMES, MinCpuField, MaxCpuField, MinRamField, MaxRamField };
