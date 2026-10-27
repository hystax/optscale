import ShareRunLinkContainer from "containers/ShareRunLinkContainer";
import BaseSideModal from "./BaseSideModal";

class ShareRunLinkModal extends BaseSideModal {
  headerProps = {
    messageId: "shareRunLinkTitle",
    dataTestIds: {
      title: "lbl_share_run_link",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_share_run_link";

  get content() {
    return <ShareRunLinkContainer runId={this.payload.runId} />;
  }
}

export default ShareRunLinkModal;
