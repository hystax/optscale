import ColumnSetsContainer from "containers/ColumnSetsContainer";
import BaseSideModal from "./BaseSideModal";

class ColumnSetsModal extends BaseSideModal {
  headerProps = {
    messageId: "columnSetsTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_column_sets_modal",
      closeButton: "bnt_close_column_sets_modal"
    }
  };

  dataTestId = "smodal_column_sets_modal";

  get content() {
    return <ColumnSetsContainer tableContext={this.payload?.tableContext} closeSideModal={this.closeSideModal} />;
  }
}

export default ColumnSetsModal;
