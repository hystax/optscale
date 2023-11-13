import Protector from "components/Protector";
import EditMlModelParameterFormContainer from "containers/EditMlModelParameterFormContainer";

const EditMlModelParameter = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <EditMlModelParameterFormContainer />
  </Protector>
);

export default EditMlModelParameter;
