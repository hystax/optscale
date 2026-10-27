import CreateResourcePerspectiveContainer from "containers/CreateResourcePerspectiveContainer";
import BaseSideModal from "./BaseSideModal";

class CreateResourcePerspectiveModal extends BaseSideModal {
  headerProps = {
    messageId: "savePerspectiveTitle",
    dataTestIds: {
      title: "lbl_save_perspective",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_save_perspective";

  get content() {
    return (
      <CreateResourcePerspectiveContainer
        breakdownBy={this.payload?.breakdownBy}
        breakdownData={this.payload?.breakdownData}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
        filterValues={this.payload?.filterValues}
        appliedFilters={this.payload?.appliedFilters}
      />
    );
  }
}

export default CreateResourcePerspectiveModal;
