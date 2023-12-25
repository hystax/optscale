import React from "react";
import MlDatasetCreateComponent from "components/MlDatasetCreate";
import Protector from "components/Protector";

const MlDatasetCreate = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlDatasetCreateComponent />
  </Protector>
);

export default MlDatasetCreate;
