import { crossRegionTraffic } from "./CrossRegionTraffic";
import { executorsReservation } from "./ExecutorsReservation";
import { executorsUpgrade } from "./ExecutorsUpgrade";
import { gpuMemory } from "./GpuMemory";
import { localStorageBottleneck } from "./LocalStorageBottleneck";
import { spotInstancesUsage } from "./SpotInstancesUsage";

const recommendationInstances = [
  executorsUpgrade,
  executorsReservation,
  spotInstancesUsage,
  crossRegionTraffic,
  localStorageBottleneck,
  gpuMemory
];

const getRecommendationInstanceByModuleName = (recommendationModuleName) =>
  recommendationInstances.find(({ moduleName }) => recommendationModuleName === moduleName);

// empty set of all possible recommendations, to show them while loading actual data
const getEmptyRecommendationsSet = () => Object.fromEntries(recommendationInstances.map(({ moduleName }) => [moduleName, {}]));

export { getRecommendationInstanceByModuleName, getEmptyRecommendationsSet };
