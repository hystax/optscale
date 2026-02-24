import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";

const Cell = ({ row: { original } }) => {
  const { cloud_account_id: dataSourceId, cloud_account_name: dataSourceName, cloud_type: dataSourceType, region } = original;

  const dataSources = useAllDataSources();

  return (
    <CaptionedCell caption={region}>
      <CloudLabel
        id={dataSourceId}
        name={dataSourceName}
        type={dataSourceType}
        disableLink={!dataSources.find(({ id }) => id === dataSourceId)}
      />
    </CaptionedCell>
  );
};

const userLocation = ({ headerDataTestId = "", accessorKey = "cloud_account_name" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: Cell,
});

export default userLocation;
