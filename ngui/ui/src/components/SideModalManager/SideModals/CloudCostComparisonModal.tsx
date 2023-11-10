import CloudCostComparisonModalContent from "components/CloudCostComparisonModalContent";
import BaseSideModal from "./BaseSideModal";

class CloudCostComparisonModal extends BaseSideModal {
  headerProps = {
    messageId: "compareSizesTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_cost_comparison",
      closeButton: "btn_cost_comparison"
    }
  };

  dataTestId = "smodal_cost_comparison";

  get content() {
    return <CloudCostComparisonModalContent onClose={this.closeSideModal} />;
  }
}

export default CloudCostComparisonModal;
