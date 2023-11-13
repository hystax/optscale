import UpdateDataSourceSkuContainer from "containers/UpdateDataSourceSkuContainer";
import BaseSideModal from "./BaseSideModal";

class UpdateDataSourceSkuModal extends BaseSideModal {
  headerProps = {
    messageId: "renameDataSourceSkuTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_update_data_source_sku",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_update_data_source_sku";

  get content() {
    return (
      <UpdateDataSourceSkuContainer
        sku={this.payload?.sku}
        cost={this.payload?.cost}
        costModel={this.payload?.costModel}
        dataSourceId={this.payload?.dataSourceId}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default UpdateDataSourceSkuModal;
