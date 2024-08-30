import { AWS_CNR, AZURE_CNR, NEBIUS } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  CLOUD_PROVIDER: "cloudProvider",
  REGION: "region",
  CURRENCY_CODE: "currency",
  MIN_CPU: "minCpu",
  MAX_CPU: "maxCpu",
  MIN_RAM: "minRam",
  MAX_RAM: "maxRam"
});

export const REGIONS = Object.freeze({
  AP: "ap",
  EU: "eu",
  CA: "ca",
  SA: "sa",
  US: "us",
  AF: "af",
  ME: "me"
});

export const SUPPORTED_CLOUD_TYPES = [
  { name: "aws", type: AWS_CNR } as const,
  {
    name: "azure",
    type: AZURE_CNR
  } as const,
  {
    name: "nebius",
    type: NEBIUS
  } as const
];
