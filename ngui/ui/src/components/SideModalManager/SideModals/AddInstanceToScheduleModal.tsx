import AddInstanceToScheduleContainer from "containers/AddInstanceToScheduleContainer";
import BaseSideModal from "./BaseSideModal";

class AddInstanceToScheduleModal extends BaseSideModal {
  headerProps = {
    messageId: "addInstancesToScheduleTitle",
    dataTestIds: {
      title: "lbl_add_instances_to_schedule_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_add_instances_to_schedule_title";

  get content() {
    return <AddInstanceToScheduleContainer powerScheduleId={this.payload?.powerScheduleId} handleClose={this.closeSideModal} />;
  }
}

export default AddInstanceToScheduleModal;
