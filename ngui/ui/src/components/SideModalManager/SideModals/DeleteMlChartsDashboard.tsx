import React from "react";
import DeleteMlChartsDashboardContainer from "containers/DeleteMlChartsDashboardContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteMlChartsDashboard extends BaseSideModal {
  headerProps = {
    messageId: "deleteDashboardTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_dashboard_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_dashboard";

  get content() {
    return (
      <DeleteMlChartsDashboardContainer
        dashboard={this.payload?.dashboard}
        removeDashboard={this.payload?.removeDashboard}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeleteMlChartsDashboard;
