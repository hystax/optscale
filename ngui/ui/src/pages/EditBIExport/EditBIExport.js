import React from "react";
import Protector from "components/Protector";
import EditBIExportContainer from "containers/EditBIExportContainer";

const EditBIExport = () => (
  <Protector allowedAction={["EDIT_PARTNER"]}>
    <EditBIExportContainer />
  </Protector>
);

export default EditBIExport;
