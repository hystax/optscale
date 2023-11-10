import Protector from "components/Protector";
import CreateEnvironmentFormContainer from "containers/CreateEnvironmentFormContainer";

const CreateEnvironment = () => (
  <Protector allowedActions={["MANAGE_RESOURCES"]}>
    <CreateEnvironmentFormContainer />
  </Protector>
);

export default CreateEnvironment;
