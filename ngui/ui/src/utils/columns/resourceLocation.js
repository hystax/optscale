import React from "react";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import ResourceLocationCell from "components/ResourceLocationCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const resourceLocation = ({
  headerDataTestId,
  idAccessor = "cloud_account_id",
  typeAccessor = "cloud_type",
  locationAccessors: {
    region: regionAccessor = "region",
    folderId: folderIdAccessor = "folder_id",
    zoneId: zoneIdAccessor = "zone_id"
  } = {},
  accessorKey: nameAccessor = "cloud_account_name"
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessorKey: nameAccessor,
  cell: ({ row: { original } }) => (
    <ResourceLocationCell
      dataSource={{
        id: original[idAccessor],
        name: original[nameAccessor],
        type: original[typeAccessor]
      }}
      caption={[
        {
          key: "region",
          node: original[regionAccessor] ? <KeyValueLabel messageId="region" value={original[regionAccessor]} /> : null
        },
        {
          key: "folderId",
          node: original[folderIdAccessor] ? <KeyValueLabel messageId="folderId" value={original[folderIdAccessor]} /> : null
        },
        {
          key: "zoneId",
          node: original[zoneIdAccessor] ? <KeyValueLabel messageId="zoneId" value={original[zoneIdAccessor]} /> : null
        }
      ].filter(({ node }) => node !== null)}
    />
  )
});

export default resourceLocation;
