import DeleteClusterTypeContainer from "containers/DeleteClusterTypeContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteClusterTypeModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteClusterTypeTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_cluster_type",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return (
      <DeleteClusterTypeContainer
        clusterTypeId={this.payload?.clusterTypeId}
        clusterTypeName={this.payload?.clusterTypeName}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeleteClusterTypeModal;
