import { RenameMlRunChartForm } from "components/forms/RenameMlRunChartForm";
import BaseSideModal from "./BaseSideModal";

class RenameMlRunChartModal extends BaseSideModal {
  headerProps = {
    messageId: "renameMlChartTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_rename_ml_run_chart",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_rename_ml_run_chart";

  get content() {
    return (
      <RenameMlRunChartForm
        chartName={this.payload?.chartName}
        onRename={(newName) => {
          this.payload?.onRename(newName);
          this.closeSideModal();
        }}
      />
    );
  }
}

export default RenameMlRunChartModal;
