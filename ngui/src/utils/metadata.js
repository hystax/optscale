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
    zone_id: zoneId
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
    { value: vpcName, messageId: METADATA_FIELDS.VPC_NAME }
  ]
    .filter(({ value }) => value !== undefined)
    .map(({ value, messageId }) => {
      if (dateTimeFields.includes(messageId)) {
        return {
          value: value === 0 ? intl.formatMessage({ id: "never" }) : formatUTC(value, EN_FORMAT),
          messageId
        };
      }
      if (messageId === METADATA_FIELDS.SIZE) {
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
