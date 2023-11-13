import { IEC_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import { intl } from "translations/react-intl-config";
import { METADATA_FIELDS } from "utils/constants";
import { EN_FORMAT, formatUTC } from "utils/datetime";

const dateTimeFields = [
  METADATA_FIELDS.FIRST_SEEN,
  METADATA_FIELDS.LAST_SEEN,
  METADATA_FIELDS.LAST_ATTACHED,
  METADATA_FIELDS.LAST_USED
];

export const MetadataNodes = ({
  first_seen: firstSeen,
  last_seen: lastSeen,
  meta: {
    attached,
    category,
    cpu_count: cpuCount,
    engine,
    engine_version: engineVersion,
    flavor,
    host_ip: hostIp,
    image_id: imageId,
    last_attached: lastAttached,
    last_used: lastUsed,
    os,
    pod_ip: podIp,
    preinstalled,
    size,
    snapshot_id: snapshotId,
    state,
    storage_type: storageType,
    volume_id: volumeId,
    volume_type: volumeType,
    vpc_id: vpcId,
    vpc_name: vpcName,
    zone_id: zoneId,
    payment_option: paymentOption,
    offering_type: offeringType,
    purchase_term: purchaseTerm,
    applied_region: appliedRegion,
    folder_id: folderId,
    source_cluster_id: sourceClusterId,
    platform_name: platformName,
    ram,
    platform_id: platformId
  } = {}
}) => {
  const formatDigitalUnit = useFormatDigitalUnit();
  const captionSettings = [
    { value: firstSeen, messageId: METADATA_FIELDS.FIRST_SEEN },
    { value: lastSeen, messageId: METADATA_FIELDS.LAST_SEEN },
    { value: imageId, messageId: METADATA_FIELDS.IMAGE_ID },
    { value: os, messageId: METADATA_FIELDS.OS },
    { value: preinstalled, messageId: METADATA_FIELDS.PREINSTALLED },
    { value: flavor, messageId: METADATA_FIELDS.FLAVOR },
    { value: cpuCount, messageId: METADATA_FIELDS.CPU_COUNT },
    { value: ram, messageId: METADATA_FIELDS.RAM },
    { value: state, messageId: METADATA_FIELDS.STATE },
    { value: zoneId, messageId: METADATA_FIELDS.ZONE_ID },
    { value: snapshotId, messageId: METADATA_FIELDS.SNAPSHOT_ID },
    { value: size, messageId: METADATA_FIELDS.SIZE },
    { value: volumeId, messageId: METADATA_FIELDS.VOLUME_ID },
    { value: engineVersion, messageId: METADATA_FIELDS.ENGINE_VERSION },
    { value: engine, messageId: METADATA_FIELDS.ENGINE },
    { value: volumeType, messageId: METADATA_FIELDS.VOLUME_TYPE },
    { value: storageType, messageId: METADATA_FIELDS.STORAGE_TYPE },
    { value: attached, messageId: METADATA_FIELDS.ATTACHED },
    { value: lastAttached, messageId: METADATA_FIELDS.LAST_ATTACHED },
    { value: lastUsed, messageId: METADATA_FIELDS.LAST_USED },
    { value: hostIp, messageId: METADATA_FIELDS.HOST_IP },
    { value: category, messageId: METADATA_FIELDS.CATEGORY },
    { value: podIp, messageId: METADATA_FIELDS.POD_IP },
    { value: vpcId, messageId: METADATA_FIELDS.VPC_ID },
    { value: vpcName, messageId: METADATA_FIELDS.VPC_NAME },
    { value: paymentOption, messageId: METADATA_FIELDS.PAYMENT_OPTION },
    { value: offeringType, messageId: METADATA_FIELDS.OFFERING_TYPE },
    { value: purchaseTerm, messageId: METADATA_FIELDS.PURCHASE_TERM },
    { value: appliedRegion, messageId: METADATA_FIELDS.APPLIED_REGION },
    { value: folderId, messageId: METADATA_FIELDS.FOLDER_ID },
    { value: sourceClusterId, messageId: METADATA_FIELDS.SOURCE_CLUSTER_ID },
    { value: platformId, messageId: METADATA_FIELDS.PLATFORM_ID },
    { value: platformName, messageId: METADATA_FIELDS.PLATFORM_NAME }
  ]
    .filter(({ value }) => value !== undefined)
    .map(({ value, messageId }) => {
      if (dateTimeFields.includes(messageId)) {
        return {
          value: value === 0 ? intl.formatMessage({ id: "never" }) : formatUTC(value, EN_FORMAT),
          messageId
        };
      }
      if ([METADATA_FIELDS.SIZE, METADATA_FIELDS.RAM].includes(messageId)) {
        return { value: formatDigitalUnit({ value, baseUnit: IEC_UNITS.BYTE, maximumFractionDigits: 1 }), messageId };
      }
      return { value: String(value), messageId };
    });

  const getTags = () =>
    Object.fromEntries(captionSettings.map(({ messageId, value }) => [intl.formatMessage({ id: messageId }), value]));

  const toString = () => captionSettings.map(({ value, messageId }) => `${intl.formatMessage({ id: messageId })}: ${value}`);

  return {
    getTags,
    toString
  };
};
