import { abandonedInstancesRecommendation } from "./AbandonedInstances";
import { abandonedKinesisStreamsRecommendation } from "./AbandonedKinesisStreams";
import { abandonedS3BucketsRecommendation } from "./AbandonedS3Buckets";
import { inactiveConsoleUsersRecommendation } from "./InactiveConsoleUsers";
import { inactiveUsersRecommendation } from "./InactiveUsers";
import { insecureSecurityGroupsRecommendation } from "./InsecureSecurityGroups";
import { instancesForShutdownRecommendation } from "./InstancesForShutdown";
import { instancesGenerationUpgradeRecommendation } from "./InstancesGenerationUpgrade";
import { instancesInStoppedStateForALongTimeRecommendation } from "./InstancesInStoppedStateForALongTime";
import { instancesMigrationRecommendation } from "./InstancesMigration";
import { instanceSubscriptionRecommendation } from "./InstanceSubscription";
import { obsoleteImagesRecommendation } from "./ObsoleteImages";
import { obsoleteIpsRecommendation } from "./ObsoleteIps";
import { obsoleteSnapshotChainsRecommendation } from "./ObsoleteSnapshotChains";
import { obsoleteSnapshotsRecommendation } from "./ObsoleteSnapshots";
import { publicS3BucketsRecommendation } from "./PublicS3Buckets";
import RelevantRecommendations from "./RelevantRecommendations";
import RelevantRecommendationsMocked from "./RelevantRecommendationsMocked";
import { reservedInstancesRecommendation } from "./ReservedInstances";
import { rightsizingInstancesRecommendation } from "./RightsizingInstances";
import { rightsizingRdsInstancesRecommendation } from "./RightsizingRdsInstances";
import { shortLivingInstancesRecommendation } from "./ShortLivingInstances";
import { volumesNotAttachedForLongTimeRecommendation } from "./VolumesNotAttachedForLongTime";

const recommendationInstances = [
  inactiveUsersRecommendation,
  inactiveConsoleUsersRecommendation,
  shortLivingInstancesRecommendation,
  volumesNotAttachedForLongTimeRecommendation,
  insecureSecurityGroupsRecommendation,
  instancesInStoppedStateForALongTimeRecommendation,
  instancesMigrationRecommendation,
  obsoleteImagesRecommendation,
  obsoleteSnapshotsRecommendation,
  obsoleteSnapshotChainsRecommendation,
  reservedInstancesRecommendation,
  instanceSubscriptionRecommendation,
  rightsizingInstancesRecommendation,
  rightsizingRdsInstancesRecommendation,
  abandonedInstancesRecommendation,
  obsoleteIpsRecommendation,
  abandonedKinesisStreamsRecommendation,
  publicS3BucketsRecommendation,
  abandonedS3BucketsRecommendation,
  instancesForShutdownRecommendation,
  instancesGenerationUpgradeRecommendation
];

// TODO: In some places we use this util with mapping BE_TO_FE_MAP_RECOMMENDATION_TYPES[recommendationType] to get recommendation instance
// We should create one more util that allows getting instances by moduleName/backendType
const getRecommendationInstanceByType = (recommendationType) =>
  recommendationInstances.find((recommendation) => recommendation.type === recommendationType);

export default RelevantRecommendations;
export { RelevantRecommendationsMocked, getRecommendationInstanceByType };
