import Protector from "components/Protector";
import CreateMlMetricFormContainer from "containers/CreateMlMetricFormContainer";

const CreateMlMetric = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <CreateMlMetricFormContainer />
  </Protector>
);

export default CreateMlMetric;
