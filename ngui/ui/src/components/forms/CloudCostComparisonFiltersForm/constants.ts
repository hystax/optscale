import { ALIBABA_CNR, AWS_CNR, AZURE_CNR, GCP_CNR, NEBIUS } from "utils/constants";

export const MIN_CPU = "1";
export const MAX_CPU = "416";
export const MIN_RAM = "0";
export const MAX_RAM = "18432";

export const FIELD_NAMES = Object.freeze({
  CLOUD_PROVIDER: "cloudProvider",
  REGION: "region",
  CURRENCY_CODE: "currency",
  MIN_CPU: "minCpu",
  MAX_CPU: "maxCpu",
  MIN_RAM: "minRam",
  MAX_RAM: "maxRam",
});

export const REGIONS = Object.freeze({
  AP: "ap",
  EU: "eu",
  CA: "ca",
  SA: "sa",
  US: "us",
  AF: "af",
  ME: "me",
});

export const SUPPORTED_CLOUD_TYPES = [
  { name: "aws", type: AWS_CNR },
  {
    name: "azure",
    type: AZURE_CNR,
  },
  {
    name: "gcp",
    type: GCP_CNR,
  },
  {
    name: "alibaba",
    type: ALIBABA_CNR,
  },
  {
    name: "nebius",
    type: NEBIUS,
  },
] as const;
