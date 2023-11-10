import RenameDataSourceContainer from "containers/RenameDataSourceContainer";
import BaseSideModal from "./BaseSideModal";

class RenameDataSourceModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "renameDataSourceTitle",
      color: "primary",
      formattedMessageValues: { name: this.payload?.name },
      dataTestIds: {
        title: "lbl_rename_data_source",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_rename_data_source";

  get content() {
    return <RenameDataSourceContainer id={this.payload?.id} name={this.payload?.name} closeSideModal={this.closeSideModal} />;
  }
}

export default RenameDataSourceModal;
