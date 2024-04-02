import Protector from "components/Protector";
import CreateMlTaskMetricFormContainer from "containers/CreateMlTaskMetricFormContainer";

const CreateMlTaskMetric = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <CreateMlTaskMetricFormContainer />
  </Protector>
);

export default CreateMlTaskMetric;
