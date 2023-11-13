import { useParams } from "react-router-dom";
import CreateAssignmentRuleFormContainer from "containers/CreateAssignmentRuleFormContainer";

const CreateAssignmentRule = () => {
  const { poolId } = useParams();

  return <CreateAssignmentRuleFormContainer poolId={poolId} />;
};

export default CreateAssignmentRule;
