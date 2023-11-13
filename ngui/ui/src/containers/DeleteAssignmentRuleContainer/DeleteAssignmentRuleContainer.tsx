import { useDispatch } from "react-redux";
import { deleteAssignmentRule } from "api";
import { DELETE_ASSIGNMENT_RULE } from "api/restapi/actionTypes";
import DeleteAssignmentRule from "components/DeleteAssignmentRule";
import { useApiSendState } from "hooks/useApiSendState";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DeleteAssignmentRuleContainer = ({ ruleId, closeSideModal }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_ASSIGNMENT_RULE);

  const { sendState, onSubmit } = useApiSendState(DELETE_ASSIGNMENT_RULE, () =>
    dispatch((_, getState) => {
      dispatch(deleteAssignmentRule(ruleId)).then(() => {
        if (!isError(DELETE_ASSIGNMENT_RULE, getState())) {
          return closeSideModal();
        }
        return Promise.reject();
      });
    })
  );

  return (
    <DeleteAssignmentRule isLoading={isLoading} closeSideModal={closeSideModal} sendState={sendState} onSubmit={onSubmit} />
  );
};

export default DeleteAssignmentRuleContainer;
