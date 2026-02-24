import { IEC_UNITS } from "components/FormattedDigitalUnit";
import { formatDigitalUnit } from "components/FormattedDigitalUnit/FormattedDigitalUnit";
import { intl } from "translations/react-intl-config";
import { METADATA_FIELDS } from "utils/constants";
import { EN_FULL_FORMAT_HH_MM_SS, formatUTC } from "utils/datetime";
import { ObjectValues } from "./types";

const formatTimestampOrNever = (value: number | string) => {
  const numberValue = Number(value);
  return numberValue === 0 ? intl.formatMessage({ id: "never" }) : formatUTC(numberValue, EN_FULL_FORMAT_HH_MM_SS);
};

const formatMetaDigitalUnit = (value: number | string) =>
  formatDigitalUnit({ value: Number(value), baseUnit: IEC_UNITS.BYTE, maximumFractionDigits: 1 });

const stringifyMetaValue = (value: unknown): string => (typeof value === "string" ? value : JSON.stringify(value));

export const metaConfig = {
  first_seen: {
    translationId: METADATA_FIELDS.FIRST_SEEN,
    format: formatTimestampOrNever,
  },
  last_seen: {
    translationId: METADATA_FIELDS.LAST_SEEN,
    format: formatTimestampOrNever,
  },
  last_attached: {
    translationId: METADATA_FIELDS.LAST_ATTACHED,
    format: formatTimestampOrNever,
  },
  last_used: {
    translationId: METADATA_FIELDS.LAST_USED,
    format: formatTimestampOrNever,
  },
  attached: { translationId: METADATA_FIELDS.ATTACHED },
  category: { translationId: METADATA_FIELDS.CATEGORY },
  cpu_count: { translationId: METADATA_FIELDS.CPU_COUNT },
  engine: { translationId: METADATA_FIELDS.ENGINE },
  engine_version: { translationId: METADATA_FIELDS.ENGINE_VERSION },
  flavor: { translationId: METADATA_FIELDS.FLAVOR },
  host_ip: { translationId: METADATA_FIELDS.HOST_IP },
  image_id: { translationId: METADATA_FIELDS.IMAGE_ID },
  os: { translationId: METADATA_FIELDS.OS },
  pod_ip: { translationId: METADATA_FIELDS.POD_IP },
  preinstalled: { translationId: METADATA_FIELDS.PREINSTALLED },
  size: {
    translationId: METADATA_FIELDS.SIZE,
    format: formatMetaDigitalUnit,
  },
  ram: {
    translationId: METADATA_FIELDS.RAM,
    format: formatMetaDigitalUnit,
  },
  snapshot_id: { translationId: METADATA_FIELDS.SNAPSHOT_ID },
  state: { translationId: METADATA_FIELDS.STATE },
  storage_type: { translationId: METADATA_FIELDS.STORAGE_TYPE },
  volume_id: { translationId: METADATA_FIELDS.VOLUME_ID },
  volume_type: { translationId: METADATA_FIELDS.VOLUME_TYPE },
  vpc_id: { translationId: METADATA_FIELDS.VPC_ID },
  vpc_name: { translationId: METADATA_FIELDS.VPC_NAME },
  zone_id: { translationId: METADATA_FIELDS.ZONE_ID },
  payment_option: { translationId: METADATA_FIELDS.PAYMENT_OPTION },
  offering_type: { translationId: METADATA_FIELDS.OFFERING_TYPE },
  purchase_term: { translationId: METADATA_FIELDS.PURCHASE_TERM },
  applied_region: { translationId: METADATA_FIELDS.APPLIED_REGION },
  folder_id: { translationId: METADATA_FIELDS.FOLDER_ID },
  source_cluster_id: { translationId: METADATA_FIELDS.SOURCE_CLUSTER_ID },
  platform_name: { translationId: METADATA_FIELDS.PLATFORM_NAME },
  platform_id: { translationId: METADATA_FIELDS.PLATFORM_ID },
  architecture: { translationId: METADATA_FIELDS.ARCHITECTURE },
  security_groups: { translationId: METADATA_FIELDS.SECURITY_GROUPS },
  stopped_allocated: { translationId: METADATA_FIELDS.STOPPED_ALLOCATED },
  last_seen_not_stopped: { translationId: METADATA_FIELDS.LAST_SEEN_NOT_STOPPED, format: formatTimestampOrNever },
  spotted: { translationId: METADATA_FIELDS.SPOTTED },
  cloud_console_link: { translationId: METADATA_FIELDS.CLOUD_CONSOLE_LINK },
  start: { translationId: METADATA_FIELDS.START, format: formatTimestampOrNever },
  end: { translationId: METADATA_FIELDS.END, format: formatTimestampOrNever },
  is_public_policy: { translationId: METADATA_FIELDS.IS_PUBLIC_POLICY },
  is_public_acls: { translationId: METADATA_FIELDS.IS_PUBLIC_ACLS },
};

const getMetaConfigByName = (name: string): ObjectValues<typeof metaConfig> | undefined =>
  metaConfig[name as keyof typeof metaConfig];

export const getMetaFormattedName = (name: string) => {
  const config = getMetaConfigByName(name);
  if (config) {
    return intl.formatMessage({ id: config.translationId });
  }
  return name;
};

export const getMetaFormattedValue = (name: string, value: string) => {
  const config = getMetaConfigByName(name);
  if (config) {
    return config.format?.(value) ?? value;
  }
  return value;
};

export const MetadataNodes = ({
  first_seen: firstSeen,
  last_seen: lastSeen,
  meta,
}: {
  first_seen: string | number;
  last_seen: string | number;
  meta: Record<string, string | number>;
}) => {
  const combinedMeta = { first_seen: firstSeen, last_seen: lastSeen, ...meta };

  const settings = Object.entries(combinedMeta)
    .filter(([, value]) => value !== undefined)
    .map(([name, value]) => {
      const config = getMetaConfigByName(name);
      if (config) {
        return {
          label: intl.formatMessage({ id: config.translationId }),
          value: config.format?.(value) ?? stringifyMetaValue(value),
        };
      }
      return { label: name, value: stringifyMetaValue(value) };
    });

  const getTags = () => Object.fromEntries(settings.map(({ label, value }) => [label, value]));

  const toString = () => settings.map(({ label, value }) => `${label}: ${value}`).join(" ");

  return {
    getTags,
    toString,
  };
};
