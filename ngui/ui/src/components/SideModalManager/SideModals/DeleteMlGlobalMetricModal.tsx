import DeleteMlGlobalMetricContainer from "containers/DeleteMlGlobalMetricContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteMlGlobalMetricModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteMetricTitle",
    color: "error",
    dataTestIds: {
      title: "title_delete_metric",
      closeButton: "close_btn"
    }
  };

  dataTestId = "smodal_delete_metric";

  get content() {
    return <DeleteMlGlobalMetricContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default DeleteMlGlobalMetricModal;
