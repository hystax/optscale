import React from "react";
import Protector from "components/Protector";
import MlEditModelContainer from "containers/MlEditModelContainer";

const MlEditModel = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlEditModelContainer />
  </Protector>
);

export default MlEditModel;
