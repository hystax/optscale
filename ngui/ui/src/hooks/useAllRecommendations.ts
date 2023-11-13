import { useMemo } from "react";
import {
  CrossRegionTraffic,
  ExecutorsReservation,
  ExecutorsUpgrade,
  GpuMemory,
  LocalStorageBottleneck,
  SpotInstancesUsage
} from "containers/RecommendationsOverviewContainer/recommendations/ml";
import { useOptscaleRecommendations } from "./useOptscaleRecommendations";

const ML_RECOMMENDATIONS = Object.fromEntries(
  [CrossRegionTraffic, ExecutorsReservation, ExecutorsUpgrade, GpuMemory, LocalStorageBottleneck, SpotInstancesUsage].map(
    (Rec) => [new Rec().type, Rec]
  )
);

export const useAllRecommendations = () => {
  const optscaleRecommendation = useOptscaleRecommendations();

  return useMemo(() => ({ ...ML_RECOMMENDATIONS, ...optscaleRecommendation }), [optscaleRecommendation]);
};
