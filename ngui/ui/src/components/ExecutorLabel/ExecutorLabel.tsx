import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { AWS_CNR, AZURE_CNR } from "utils/constants";

// ML profiling: map cloud types to OptScale data source types
const PLATFORM_TYPE_TO_DATA_SOURCE_TYPE = Object.freeze({
  azure: AZURE_CNR,
  aws: AWS_CNR
});

const DiscoveredExecutorLabel = ({ resource }) => {
  const { _id: id, cloud_resource_id: cloudResourceId, cloud_account: { type } = {} } = resource;

  return (
    <IconLabel
      icon={<CloudTypeIcon type={type} hasRightMargin />}
      label={<CloudResourceId resourceId={id} cloudResourceIdentifier={cloudResourceId} />}
    />
  );
};

const ExecutorLabel = ({ instanceId, platformType, discovered = false, resource }) =>
  discovered ? (
    <DiscoveredExecutorLabel resource={resource} />
  ) : (
    <IconLabel
      icon={<CloudTypeIcon type={PLATFORM_TYPE_TO_DATA_SOURCE_TYPE[platformType]} hasRightMargin />}
      label={<CloudResourceId cloudResourceIdentifier={instanceId} disableLink={!discovered} />}
    />
  );

export default ExecutorLabel;
