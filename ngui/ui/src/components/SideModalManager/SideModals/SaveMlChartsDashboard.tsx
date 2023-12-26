import SaveMlChartsDashboardFormContainer from "containers/SaveMlChartsDashboardFormContainer";
import BaseSideModal from "./BaseSideModal";

class SaveMlChartsDashboard extends BaseSideModal {
  headerProps = {
    messageId: "saveDashboard",
    dataTestIds: {
      title: "lbl_save_dashboard",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_save_dashboard";

  get content() {
    return (
      <SaveMlChartsDashboardFormContainer
        dashboard={this.payload?.dashboard}
        updateDashboard={this.payload?.updateDashboard}
        createDashboard={this.payload?.createDashboard}
        isOwnedDashboard={this.payload?.isOwnedDashboard}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default SaveMlChartsDashboard;
