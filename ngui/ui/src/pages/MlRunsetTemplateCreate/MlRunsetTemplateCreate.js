import React from "react";
import MlRunsetTemplateCreateComponent from "components/MlRunsetTemplateCreate";
import Protector from "components/Protector";

const MlRunsetTemplateCreate = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlRunsetTemplateCreateComponent />
  </Protector>
);

export default MlRunsetTemplateCreate;
