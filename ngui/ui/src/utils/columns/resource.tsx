import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudResourceId from "components/CloudResourceId";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { getCloudResourceIdentifier } from "utils/resources";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

type CellRowData = { resource_name: string; resource_id: string; cloud_account_id: string };

type ResourceColumnConfig = {
  headerDataTestId?: string;
  id?: string;
};

const CellContent = ({ rowData }: { rowData: CellRowData }) => {
  const { resource_name: name, resource_id: resourceId, cloud_account_id: dataSourceId } = rowData;

  const dataSources = useAllDataSources();

  return (
    <CaptionedCell caption={name}>
      <CloudResourceId
        disableLink={!dataSources.find(({ id }) => id === dataSourceId)}
        resourceId={resourceId}
        cloudResourceIdentifier={getCloudResourceIdentifier(rowData)}
        dataSourceId={dataSourceId}
      />
    </CaptionedCell>
  );
};

const resource = ({ headerDataTestId, id = "cloudResourceIdentifier" }: ResourceColumnConfig = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="resource" />
    </TextWithDataTestId>
  ),
  id,
  style: RESOURCE_ID_COLUMN_CELL_STYLE,
  cell: ({ row: { original } }: { row: { original: CellRowData } }) => <CellContent rowData={original} />,
});

export default resource;
