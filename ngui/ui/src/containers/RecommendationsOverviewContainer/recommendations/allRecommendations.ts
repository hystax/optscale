import AbandonedImages from "./AbandonedImages";
import AbandonedInstances from "./AbandonedInstances";
import AbandonedKinesisStreams from "./AbandonedKinesisStreams";
import AbandonedNebiusS3Buckets from "./AbandonedNebiusS3Buckets";
import AbandonedS3Buckets from "./AbandonedS3Buckets";
import CvocAgreementOpportunities from "./CvocAgreementOpportunities";
import InactiveConsoleUsers from "./InactiveConsoleUsers";
import InactiveUsers from "./InactiveUsers";
import InsecureSecurityGroups from "./InsecureSecurityGroups";
import InstancesForShutdown from "./InstancesForShutdown";
import InstancesGenerationUpgrade from "./InstancesGenerationUpgrade";
import InstancesInStoppedStateForALongTime from "./InstancesInStoppedStateForALongTime";
import InstancesMigration from "./InstancesMigration";
import InstanceSubscription from "./InstanceSubscription";
import {
  CrossRegionTraffic,
  ExecutorsReservation,
  ExecutorsUpgrade,
  GpuMemory,
  LocalStorageBottleneck,
  SpotInstancesUsage
} from "./ml";
import ObsoleteImages from "./ObsoleteImages";
import ObsoleteIps from "./ObsoleteIps";
import ObsoleteSnapshotChains from "./ObsoleteSnapshotChains";
import ObsoleteSnapshots from "./ObsoleteSnapshots";
import PublicS3Buckets from "./PublicS3Buckets";
import ReservedInstances from "./ReservedInstances";
import RightsizingInstances from "./RightsizingInstances";
import RightsizingRdsInstances from "./RightsizingRdsInstances";
import ShortLivingInstances from "./ShortLivingInstances";
import VolumesNotAttachedForLongTime from "./VolumesNotAttachedForLongTime";

const ML_RECOMMENDATIONS = Object.fromEntries(
  [CrossRegionTraffic, ExecutorsReservation, ExecutorsUpgrade, GpuMemory, LocalStorageBottleneck, SpotInstancesUsage].map(
    (Rec) => [new Rec().type, Rec]
  )
);

export const OPTSCALE_RECOMMENDATIONS = Object.fromEntries(
  [
    VolumesNotAttachedForLongTime,
    ShortLivingInstances,
    RightsizingRdsInstances,
    RightsizingInstances,
    ReservedInstances,
    ObsoleteSnapshots,
    ObsoleteSnapshotChains,
    ObsoleteIps,
    InstanceSubscription,
    InstancesMigration,
    InstancesInStoppedStateForALongTime,
    InstancesGenerationUpgrade,
    InstancesForShutdown,
    InsecureSecurityGroups,
    InactiveUsers,
    InactiveConsoleUsers,
    AbandonedS3Buckets,
    AbandonedKinesisStreams,
    AbandonedInstances,
    PublicS3Buckets,
    ObsoleteImages,
    AbandonedImages,
    AbandonedNebiusS3Buckets,
    CvocAgreementOpportunities
  ].map((Rec) => [new Rec().type, Rec])
);

export const ALL_RECOMMENDATIONS = { ...ML_RECOMMENDATIONS, ...OPTSCALE_RECOMMENDATIONS };
