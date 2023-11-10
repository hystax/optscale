import { useDispatch } from "react-redux";
import { updateAssignmentRulePriority } from "api";
import { UPDATE_ASSIGNMENT_RULE_PRIORITY } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";

const useUpdate = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ASSIGNMENT_RULE_PRIORITY);

  const updatePriority = (assignmentRuleId, action) => {
    dispatch(updateAssignmentRulePriority(assignmentRuleId, action));
  };

  return { isLoading, updatePriority };
};

function AssignmentRulePriorityService() {
  return { useUpdate };
}

export default AssignmentRulePriorityService;
