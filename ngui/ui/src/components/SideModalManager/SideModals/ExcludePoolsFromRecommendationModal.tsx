import { FormattedMessage } from "react-intl";
import ExcludePoolsFromRecommendation from "components/ExcludePoolsFromRecommendation";
import BaseSideModal from "./BaseSideModal";

class ExcludePoolsFromRecommendationModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "excludePoolsFromRecommendationTitle",
      formattedMessageValues: { recommendation: <FormattedMessage id={this.payload.recommendationName} /> },
      dataTestIds: {
        title: "lbl_exclude_pools_sidemodal_title",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_exclude_pools";

  get content() {
    return (
      <ExcludePoolsFromRecommendation onSuccess={this.closeSideModal} recommendationType={this.payload?.recommendationType} />
    );
  }
}

export default ExcludePoolsFromRecommendationModal;
