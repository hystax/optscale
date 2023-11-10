import ReapplyClusterTypesContainer from "containers/ReapplyClusterTypesContainer";
import BaseSideModal from "./BaseSideModal";

class ReapplyClusterTypesModal extends BaseSideModal {
  headerProps = {
    messageId: "reapplyClusterTypesTitle",
    dataTestIds: {
      title: "lbl_re_apply_cluster_types",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_reapply";

  get content() {
    return <ReapplyClusterTypesContainer onCancel={this.closeSideModal} />;
  }
}

export default ReapplyClusterTypesModal;
