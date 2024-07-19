import { useMemo } from "react";
import AbandonedImages from "containers/RecommendationsOverviewContainer/recommendations/AbandonedImages";
import AbandonedInstances from "containers/RecommendationsOverviewContainer/recommendations/AbandonedInstances";
import AbandonedKinesisStreams from "containers/RecommendationsOverviewContainer/recommendations/AbandonedKinesisStreams";
import AbandonedNebiusS3Buckets from "containers/RecommendationsOverviewContainer/recommendations/AbandonedNebiusS3Buckets";
import AbandonedS3Buckets from "containers/RecommendationsOverviewContainer/recommendations/AbandonedS3Buckets";
import CvocAgreementOpportunities from "containers/RecommendationsOverviewContainer/recommendations/CvocAgreementOpportunities";
import InactiveConsoleUsers from "containers/RecommendationsOverviewContainer/recommendations/InactiveConsoleUsers";
import InactiveUsers from "containers/RecommendationsOverviewContainer/recommendations/InactiveUsers";
import InsecureSecurityGroups from "containers/RecommendationsOverviewContainer/recommendations/InsecureSecurityGroups";
import InstancesForShutdown from "containers/RecommendationsOverviewContainer/recommendations/InstancesForShutdown";
import InstancesGenerationUpgrade from "containers/RecommendationsOverviewContainer/recommendations/InstancesGenerationUpgrade";
import InstancesInStoppedStateForALongTime from "containers/RecommendationsOverviewContainer/recommendations/InstancesInStoppedStateForALongTime";
import InstancesMigration from "containers/RecommendationsOverviewContainer/recommendations/InstancesMigration";
import InstanceSubscription from "containers/RecommendationsOverviewContainer/recommendations/InstanceSubscription";
import NebiusMigration from "containers/RecommendationsOverviewContainer/recommendations/NebiusMigration";
import ObsoleteImages from "containers/RecommendationsOverviewContainer/recommendations/ObsoleteImages";
import ObsoleteIps from "containers/RecommendationsOverviewContainer/recommendations/ObsoleteIps";
import ObsoleteSnapshotChains from "containers/RecommendationsOverviewContainer/recommendations/ObsoleteSnapshotChains";
import ObsoleteSnapshots from "containers/RecommendationsOverviewContainer/recommendations/ObsoleteSnapshots";
import PublicS3Buckets from "containers/RecommendationsOverviewContainer/recommendations/PublicS3Buckets";
import ReservedInstances from "containers/RecommendationsOverviewContainer/recommendations/ReservedInstances";
import RightsizingInstances from "containers/RecommendationsOverviewContainer/recommendations/RightsizingInstances";
import RightsizingRdsInstances from "containers/RecommendationsOverviewContainer/recommendations/RightsizingRdsInstances";
import ShortLivingInstances from "containers/RecommendationsOverviewContainer/recommendations/ShortLivingInstances";
import VolumesNotAttachedForLongTime from "containers/RecommendationsOverviewContainer/recommendations/VolumesNotAttachedForLongTime";
import { useIsNebiusConnectionEnabled } from "hooks/useIsNebiusConnectionEnabled";

const NEBIUS_RECOMMENDATIONS = [AbandonedImages, CvocAgreementOpportunities, AbandonedNebiusS3Buckets, NebiusMigration];

export const NEBIUS_RECOMMENDATION_TYPES = NEBIUS_RECOMMENDATIONS.map((Recommendation) => new Recommendation().type);

export const useOptscaleRecommendations = () => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  return useMemo(() => {
    const recommendations = [
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
      ...(isNebiusConnectionEnabled ? NEBIUS_RECOMMENDATIONS : [])
    ];

    return Object.fromEntries(recommendations.map((Rec) => [new Rec().type, Rec]));
  }, [isNebiusConnectionEnabled]);
};
