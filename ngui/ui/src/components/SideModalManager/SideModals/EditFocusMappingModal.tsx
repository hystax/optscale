import EditFocusMappingContainer from "containers/EditFocusMappingContainer";
import BaseSideModal from "./BaseSideModal";

class EditFocusMappingModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "editFocusMappingTitle",
      color: "primary",
      showExpand: true,
      formattedMessageValues: { name: this.payload?.name },
      dataTestIds: {
        title: "lbl_edit_focus_mapping",
        closeButton: "btn_close",
      },
    };
  }

  dataTestId = "smodal_edit_focus_mapping";

  get content() {
    return (
      <EditFocusMappingContainer
        id={this.payload?.id}
        mapping={this.payload?.config?.mapping}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default EditFocusMappingModal;
