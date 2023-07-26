import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const getMessageId = (resourceType) =>
  ({
    instance: "resourceType.instance",
    volume: "resourceType.volume",
    snapshot: "resourceType.snapshot",
    bucket: "resourceType.bucket",
    k8s_pod: "resourceType.k8sPod",
    snapshot_chain: "resourceType.snapshotChain",
    rds_instance: "resourceType.rdsInstance",
    ip_address: "resourceType.ipAddress",
    image: "resourceType.image"
  }[resourceType]);

const resourceType = ({
  headerDataTestId = "lbl_resource_type",
  messageId = "resourceType",
  accessorKey = "resource_type",
  style = {}
} = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  style,
  cell: ({ cell }) => {
    const type = cell.getValue();

    const typeTranslationMessageId = getMessageId(type);

    return typeTranslationMessageId ? <FormattedMessage id={typeTranslationMessageId} /> : type;
  }
});

export default resourceType;
