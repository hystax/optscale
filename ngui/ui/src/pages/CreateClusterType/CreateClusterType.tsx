import Protector from "components/Protector";
import CreateClusterTypeFormContainer from "containers/CreateClusterTypeFormContainer";

const CreateClusterType = () => (
  <Protector allowedActions={["MANAGE_RESOURCES"]}>
    <CreateClusterTypeFormContainer />
  </Protector>
);

export default CreateClusterType;
