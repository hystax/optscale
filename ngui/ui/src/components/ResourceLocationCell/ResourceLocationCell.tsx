import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import { useApiData } from "hooks/useApiData";

const ResourceLocationCell = ({ dataSource, caption }) => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  return (
    <CaptionedCell caption={caption}>
      <CloudLabel
        disableLink={!dataSources.find(({ id }) => id === dataSource.id)}
        id={dataSource.id}
        name={dataSource.name}
        type={dataSource.type}
      />
    </CaptionedCell>
  );
};

export default ResourceLocationCell;
