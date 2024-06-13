import { useDispatch } from "react-redux";
import { calendarSynchronization } from "api";
import { CALENDAR_SYNCHRONIZATION } from "api/restapi/actionTypes";
import ConnectGoogleCalendarForm from "components/forms/ConnectGoogleCalendarForm";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const ConnectGoogleCalendarContainer = ({ serviceAccount, onCancel }) => {
  const { isLoading } = useApiState(CALENDAR_SYNCHRONIZATION);
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const onSubmit = (calendarId) =>
    dispatch((_, getState) => {
      dispatch(calendarSynchronization(organizationId, calendarId)).then(() => {
        if (!isError(CALENDAR_SYNCHRONIZATION, getState())) {
          onCancel();
        }
      });
    });

  return (
    <ConnectGoogleCalendarForm isLoading={isLoading} serviceAccount={serviceAccount} onCancel={onCancel} onSubmit={onSubmit} />
  );
};

export default ConnectGoogleCalendarContainer;
