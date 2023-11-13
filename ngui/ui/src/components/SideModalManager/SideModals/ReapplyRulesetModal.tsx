import ReapplyRulesetFormContainer from "containers/ReapplyRulesetFormContainer";
import BaseSideModal from "./BaseSideModal";

class ReapplyRulesetModal extends BaseSideModal {
  headerProps = {
    messageId: "reapplyRulesetTitle",
    dataTestIds: {
      title: "title_reapply",
      closeButton: "close_btn"
    }
  };

  dataTestId = "smodal_reapply_ruleset";

  get content() {
    return <ReapplyRulesetFormContainer closeSideModal={this.closeSideModal} />;
  }
}

export default ReapplyRulesetModal;
