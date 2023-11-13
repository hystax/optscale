import Protector from "components/Protector";
import CreateMlModelParameterFormContainer from "containers/CreateMlModelParameterFormContainer";

const CreateMlModelParameter = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <CreateMlModelParameterFormContainer />
  </Protector>
);

export default CreateMlModelParameter;
