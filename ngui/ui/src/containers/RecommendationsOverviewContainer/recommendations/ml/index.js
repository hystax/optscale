import CrossRegionTraffic from "./CrossRegionTraffic";
import ExecutorsReservation from "./ExecutorsReservation";
import ExecutorsUpgrade from "./ExecutorsUpgrade";
import GpuMemory from "./GpuMemory";
import LocalStorageBottleneck from "./LocalStorageBottleneck";
import SpotInstancesUsage from "./SpotInstancesUsage";

const ML_RECOMMENDATIONS = Object.fromEntries(
  [CrossRegionTraffic, ExecutorsReservation, ExecutorsUpgrade, GpuMemory, LocalStorageBottleneck, SpotInstancesUsage].map(
    (Rec) => [new Rec().type, Rec]
  )
);

export {
  ML_RECOMMENDATIONS,
  CrossRegionTraffic,
  ExecutorsReservation,
  ExecutorsUpgrade,
  GpuMemory,
  LocalStorageBottleneck,
  SpotInstancesUsage
};
