import React from "react";
import UpdateDataSourceCredentialsContainer from "containers/UpdateDataSourceCredentialsContainer";
import BaseSideModal from "./BaseSideModal";

class UpdateDataSourceCredentialsModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "updateDataSourceCredentials",
      color: "primary",
      formattedMessageValues: { name: this.payload?.name },
      dataTestIds: {
        title: "lbl_update_data_source_credentials",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_update_data_source_credentials";

  get content() {
    return (
      <UpdateDataSourceCredentialsContainer
        id={this.payload?.id}
        name={this.payload?.type}
        type={this.payload?.type}
        config={this.payload?.config}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default UpdateDataSourceCredentialsModal;
