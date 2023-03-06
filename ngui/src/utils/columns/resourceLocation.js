import React from "react";
import { FormattedMessage } from "react-intl";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useApiData } from "hooks/useApiData";

const CellContent = ({ dataSourceId, dataSourceName, dataSourceType, region }) => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  return (
    <CaptionedCell caption={region}>
      <CloudLabel
        disableLink={!dataSources.find(({ id }) => id === dataSourceId)}
        id={dataSourceId}
        name={dataSourceName}
        type={dataSourceType}
      />
    </CaptionedCell>
  );
};

const resourceLocation = ({
  headerDataTestId,
  idAccessor = "cloud_account_id",
  typeAccessor = "cloud_type",
  regionAccessor = "region",
  accessorKey: nameAccessor = "cloud_account_name"
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessorKey: nameAccessor,
  cell: ({ row: { original } }) => (
    <CellContent
      dataSourceId={original[idAccessor]}
      dataSourceName={original[nameAccessor]}
      dataSourceType={original[typeAccessor]}
      region={original[regionAccessor]}
    />
  )
});

export default resourceLocation;
