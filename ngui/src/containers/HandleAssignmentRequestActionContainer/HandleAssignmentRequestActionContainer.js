import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { assignmentRequestUpdate, getMyTasks } from "api";
import { ASSIGNMENT_REQUEST_UPDATE } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { MAP_MY_TASKS_TYPES } from "utils/constants";
import { getQueryParams } from "utils/network";

const assignmentRequestUpdateWithMyTasksRequest = (assignmentObject, myTasksObject) => (dispatch, getState) => {
  dispatch(assignmentRequestUpdate(assignmentObject)).then(() => {
    if (!isError(ASSIGNMENT_REQUEST_UPDATE, getState())) {
      dispatch(getMyTasks(myTasksObject));
    }
  });
};

const HandleAssignmentRequestActionContainer = ({ requestId, action, children }) => {
  const queryParams = getQueryParams();
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading, entityId } = useApiState(ASSIGNMENT_REQUEST_UPDATE, requestId);

  const onAssign = () => {
    dispatch(
      assignmentRequestUpdateWithMyTasksRequest(
        {
          requestId,
          action
        },
        {
          organizationId,
          type: queryParams.task ? MAP_MY_TASKS_TYPES[queryParams.task] : undefined
        }
      )
    );
  };

  return React.cloneElement(children, {
    onClick: onAssign,
    isLoading: requestId === entityId ? isLoading : false
  });
};

HandleAssignmentRequestActionContainer.propTypes = {
  requestId: PropTypes.string.isRequired,
  action: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired
};

export default HandleAssignmentRequestActionContainer;
