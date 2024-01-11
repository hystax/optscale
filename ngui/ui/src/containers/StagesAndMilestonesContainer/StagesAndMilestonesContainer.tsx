import { getMilestoneTuplesGroupedByTime } from "components/ExecutionBreakdown/utils";
import StagesAndMilestones from "components/StagesAndMilestones";
import { getData } from "containers/ExecutionBreakdownContainer/utils";
import MlModelsService from "services/MlModelsService";

const StagesAndMilestonesContainer = ({
  runId,
  closeSideModal,
  highlightedStage,
  setHighlightedStage,
  setSelectedSegment,
  secondsTimeRange
}) => {
  const { useGetRunBreakdown } = MlModelsService();

  const { breakdown = {}, milestones: milestonesApi = [], stages: stagesApi = [] } = useGetRunBreakdown(runId);

  const { stages, milestones } = getData({ breakdown, milestones: milestonesApi, stages: stagesApi });

  const milestonesGroupedByTimeTuples = getMilestoneTuplesGroupedByTime(milestones);

  return (
    <StagesAndMilestones
      milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
      resetBrushTo={(start, end) => {
        setSelectedSegment([start, end]);
        closeSideModal();
      }}
      stages={stages}
      highlightedStage={highlightedStage}
      setHighlightedStage={(stage) => {
        setHighlightedStage(stage);
        closeSideModal();
      }}
      secondsTimeRange={secondsTimeRange}
    />
  );
};

export default StagesAndMilestonesContainer;
