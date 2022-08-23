import React from "react";
import DeleteEmployeeContainer from "containers/DeleteEmployeeContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteEmployeeModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteUserTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_employee",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_employee";

  get content() {
    return (
      <DeleteEmployeeContainer
        employees={this.payload?.employees}
        entityToBeDeleted={this.payload?.entityToBeDeleted}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default DeleteEmployeeModal;
