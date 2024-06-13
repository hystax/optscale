import { FIELD_NAMES } from "./constants";

export const getDefaultValues = ({
  cloudProvider,
  region,
  currency,
  minCpu,
  maxCpu,
  minRam,
  maxRam
}: {
  cloudProvider: string;
  region: string;
  currency: string;
  minCpu: string;
  maxCpu: string;
  minRam: string;
  maxRam: string;
}) => ({
  [FIELD_NAMES.CLOUD_PROVIDER]: cloudProvider,
  [FIELD_NAMES.REGION]: region,
  [FIELD_NAMES.CURRENCY_CODE]: currency,
  [FIELD_NAMES.MIN_CPU]: minCpu,
  [FIELD_NAMES.MAX_CPU]: maxCpu,
  [FIELD_NAMES.MIN_RAM]: minRam,
  [FIELD_NAMES.MAX_RAM]: maxRam
});
