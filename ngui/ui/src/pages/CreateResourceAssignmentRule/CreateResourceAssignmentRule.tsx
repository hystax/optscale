import { useParams } from "react-router-dom";
import CreateResourceAssignmentRuleFormContainer from "containers/CreateResourceAssignmentRuleFormContainer";

const CreateResourceAssignmentRule = () => {
  const { resourceId } = useParams();

  return <CreateResourceAssignmentRuleFormContainer resourceId={resourceId} />;
};

export default CreateResourceAssignmentRule;
