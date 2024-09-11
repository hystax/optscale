import Protector from "components/Protector";
import EditMlMetricFormContainer from "containers/EditMlMetricFormContainer";

const EditMlMetric = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <EditMlMetricFormContainer />
  </Protector>
);

export default EditMlMetric;
