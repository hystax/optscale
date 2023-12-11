import RemoveInstancesFromScheduleContainer from "containers/RemoveInstancesFromScheduleContainer";
import BaseSideModal from "./BaseSideModal";

class RemoveInstancesFromScheduleModal extends BaseSideModal {
  headerProps = {
    messageId: "removeInstancesFromScheduleTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_remove_instances_from_schedule_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_remove_instances_from_schedule_title";

  get content() {
    return (
      <RemoveInstancesFromScheduleContainer
        powerScheduleId={this.payload?.powerScheduleId}
        instancesToRemove={this.payload?.selectedInstances}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default RemoveInstancesFromScheduleModal;
