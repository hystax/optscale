import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { useApiData } from "hooks/useApiData";
import { getCloudResourceIdentifier } from "utils/resources";

const RecommendationListItemResourceLabel = ({ item }) => {
  const { cloud_type: cloudType, cloud_account_id: dataSourceId, resource_id: resourceId } = item;

  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  return (
    <IconLabel
      icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
      label={
        <CloudResourceId
          disableLink={!dataSources.find(({ id }) => id === dataSourceId)}
          resourceId={resourceId}
          cloudResourceIdentifier={getCloudResourceIdentifier(item)}
          dataSourceId={dataSourceId}
        />
      }
    />
  );
};

export default RecommendationListItemResourceLabel;
