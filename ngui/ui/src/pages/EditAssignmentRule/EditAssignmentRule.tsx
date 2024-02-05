import { useParams } from "react-router-dom";
import EditAssignmentRuleFormContainer from "containers/EditAssignmentRuleFormContainer";

const EditAssignmentRule = () => {
  const { assignmentRuleId, poolId } = useParams();

  return <EditAssignmentRuleFormContainer assignmentRuleId={assignmentRuleId} poolId={poolId} />;
};

export default EditAssignmentRule;
