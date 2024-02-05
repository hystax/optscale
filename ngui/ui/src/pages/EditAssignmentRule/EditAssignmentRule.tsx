import { useParams } from "react-router-dom";
import EditAssignmentRuleFormContainer from "containers/EditAssignmentRuleFormContainer";

const EditAssignmentRule = () => {
  const { assignmentRuleId } = useParams();

  return <EditAssignmentRuleFormContainer assignmentRuleId={assignmentRuleId} />;
};

export default EditAssignmentRule;
