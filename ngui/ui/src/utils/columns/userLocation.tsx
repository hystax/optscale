import { FormattedMessage } from "react-intl";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useApiData } from "hooks/useApiData";

const Cell = ({
  row: {
    original: { cloud_account_id: dataSourceId, cloud_account_name: dataSourceName, cloud_type: dataSourceType, region }
  }
}) => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

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
  cell: Cell
});

export default userLocation;
