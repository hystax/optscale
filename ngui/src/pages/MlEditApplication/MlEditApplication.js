import React from "react";
import Protector from "components/Protector";
import MlEditApplicationContainer from "containers/MlEditApplicationContainer";

const MlEditApplication = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlEditApplicationContainer />
  </Protector>
);

export default MlEditApplication;
