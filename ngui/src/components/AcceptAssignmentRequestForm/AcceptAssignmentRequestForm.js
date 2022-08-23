import React from "react";
import PropTypes from "prop-types";
import { useForm, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import { useSelector, useDispatch } from "react-redux";
import { assignmentRequestUpdate, getMyTasks } from "api";
import { ASSIGNMENT_REQUEST_UPDATE } from "api/restapi/actionTypes";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import KeyValueLabel from "components/KeyValueLabel";
import AvailablePoolSelectorContainer from "containers/AvailablePoolSelectorContainer";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { ACCEPT, REQUESTED, MAP_MY_TASKS_TYPES } from "utils/constants";
import { getQueryParams } from "utils/network";

const POOL_ID = "poolId";

const assignmentRequestUpdateWithMyTasksRequest = (assignmentObject, myTasksObject, closeSideModal) => (dispatch, getState) => {
  dispatch(assignmentRequestUpdate(assignmentObject)).then(() => {
    if (!isError(ASSIGNMENT_REQUEST_UPDATE, getState())) {
      dispatch(getMyTasks(myTasksObject));
      closeSideModal();
    }
  });
};

// TODO: We will remove this component when we can add the AvailablePoolSelectorContainer to the table row.
const AcceptAssignmentRequestForm = ({ assignmentRequestId, resourceName, closeSideModal }) => {
  const queryParams = getQueryParams();
  const intl = useIntl();
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const resourcesState = useSelector((state) => state.resources) || {};
  const { [REQUESTED]: { poolId = "" } = {} } = resourcesState;
  const {
    handleSubmit,
    control,
    formState: { errors }
  } = useForm();
  const { isLoading } = useApiState(ASSIGNMENT_REQUEST_UPDATE, assignmentRequestId);

  const onSubmit = () =>
    dispatch(
      assignmentRequestUpdateWithMyTasksRequest(
        {
          requestId: assignmentRequestId,
          action: ACCEPT,
          poolId
        },
        {
          organizationId,
          type: MAP_MY_TASKS_TYPES[queryParams?.task]
        },
        closeSideModal
      )
    );

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <KeyValueLabel messageId="resourceName" value={resourceName} />
      <Controller
        name={POOL_ID}
        control={control}
        rules={{
          validate: () => (!resourcesState?.requested?.[POOL_ID] ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
        }}
        defaultValue=""
        render={() => (
          <AvailablePoolSelectorContainer
            splitGroup={REQUESTED}
            error={!!errors[POOL_ID]}
            helperText={errors?.[POOL_ID]?.message}
          />
        )}
      />
      <FormButtonsWrapper withBottomMargin>
        <ButtonLoader variant="contained" color="primary" messageId={ACCEPT} type="submit" isLoading={isLoading} />
      </FormButtonsWrapper>
    </form>
  );
};

AcceptAssignmentRequestForm.propTypes = {
  assignmentRequestId: PropTypes.string.isRequired,
  resourceName: PropTypes.string,
  closeSideModal: PropTypes.func.isRequired
};

export default AcceptAssignmentRequestForm;
