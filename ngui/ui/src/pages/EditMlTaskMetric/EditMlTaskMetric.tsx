import Protector from "components/Protector";
import EditMlTaskMetricFormContainer from "containers/EditMlTaskMetricFormContainer";

const EditMlTaskMetric = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <EditMlTaskMetricFormContainer />
  </Protector>
);

export default EditMlTaskMetric;
