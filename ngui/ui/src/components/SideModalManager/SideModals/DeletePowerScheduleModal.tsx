import DeletePowerScheduleContainer from "containers/DeletePowerScheduleContainer";
import BaseSideModal from "./BaseSideModal";

class DeletePowerScheduleModal extends BaseSideModal {
  headerProps = {
    messageId: "deletePowerScheduleTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_power_schedule",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_power_schedule";

  get content() {
    return (
      <DeletePowerScheduleContainer id={this.payload?.id} name={this.payload?.name} closeSideModal={this.closeSideModal} />
    );
  }
}

export default DeletePowerScheduleModal;
