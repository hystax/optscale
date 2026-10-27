import DataSourceBillingReimportContainer from "containers/DataSourceBillingReimportContainer/DataSourceBillingReimportContainer";
import BaseSideModal from "./BaseSideModal";

class DataSourceBillingReimportModal extends BaseSideModal {
  headerProps = {
    messageId: "billingReimportTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_reimport_data_source_expenses",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_reimport_data_source_expenses";

  get content() {
    return <DataSourceBillingReimportContainer dataSourceId={this.payload?.id} onSuccess={this.closeSideModal} />;
  }
}

export default DataSourceBillingReimportModal;
