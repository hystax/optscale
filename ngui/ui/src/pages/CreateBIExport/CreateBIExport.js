import React from "react";
import Protector from "components/Protector";
import CreateBIExportContainer from "containers/CreateBIExportContainer";

const CreateBIExport = () => (
  <Protector allowedAction={["EDIT_PARTNER"]}>
    <CreateBIExportContainer />
  </Protector>
);

export default CreateBIExport;
