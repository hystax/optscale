import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import ResourceLocationCell from "components/ResourceLocationCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { intl } from "translations/react-intl-config";

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
  ),
  globalFilterFn: (_, filterValue, { row: { original } }) => {
    const { [nameAccessor]: name, [regionAccessor]: region, [folderIdAccessor]: folderId, [zoneIdAccessor]: zoneId } = original;

    const search = filterValue.toLocaleLowerCase();

    return [
      name,
      `${intl.formatMessage({ id: "region" })}: ${region}`,
      `${intl.formatMessage({ id: "folderId" })}: ${folderId}`,
      `${intl.formatMessage({ id: "zoneId" })}: ${zoneId}`
    ]
      .join(" ")
      .toLocaleLowerCase()
      .includes(search);
  }
});

export default resourceLocation;
