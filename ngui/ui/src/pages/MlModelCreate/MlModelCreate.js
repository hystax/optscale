import React from "react";
import MlModelCreateComponent from "components/MlModelCreate";
import Protector from "components/Protector";

const MlModelCreate = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlModelCreateComponent />
  </Protector>
);

export default MlModelCreate;
