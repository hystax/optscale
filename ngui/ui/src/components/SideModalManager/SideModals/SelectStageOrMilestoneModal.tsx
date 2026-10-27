import StagesAndMilestones from "components/StagesAndMilestones";
import BaseSideModal from "./BaseSideModal";

class SelectStageOrMilestoneModal extends BaseSideModal {
  headerProps = {
    messageId: "selectStageOrMilestone",
    dataTestIds: {
      title: "lbl_select_stage_or_milestone",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_select_stage_or_milestone";

  get content() {
    const {
      highlightedStage,
      setHighlightedStage,
      setSelectedSegment,
      secondsTimeRange,
      stages,
      milestonesGroupedByTimeTuples,
    } = this.payload;

    return (
      <StagesAndMilestones
        milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
        resetBrushTo={(start, end) => {
          setSelectedSegment([start, end]);
          this.closeSideModal();
        }}
        stages={stages}
        highlightedStage={highlightedStage}
        setHighlightedStage={(stage) => {
          setHighlightedStage(stage);
          this.closeSideModal();
        }}
        secondsTimeRange={secondsTimeRange}
      />
    );
  }
}

export default SelectStageOrMilestoneModal;
