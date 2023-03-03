import React from "react";
import Protector from "components/Protector";
import CreateMlApplicationParameterFormContainer from "containers/CreateMlApplicationParameterFormContainer";

const CreateMlApplicationParameter = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <CreateMlApplicationParameterFormContainer />
  </Protector>
);

export default CreateMlApplicationParameter;
