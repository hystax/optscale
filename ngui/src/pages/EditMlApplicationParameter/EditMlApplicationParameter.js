import React from "react";
import Protector from "components/Protector";
import EditMlApplicationParameterFormContainer from "containers/EditMlApplicationParameterFormContainer";

const EditMlApplicationParameter = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <EditMlApplicationParameterFormContainer />
  </Protector>
);

export default EditMlApplicationParameter;
