import GoogleCalendar from "components/Integrations/GoogleCalendar";
import OrganizationCalendarService from "services/OrganizationCalendarService";

const IntegrationsGoogleCalendarContainer = () => {
  const { useGet } = OrganizationCalendarService();

  const {
    isLoading,
    organizationCalendar: { service_account: serviceAccount, calendar_synchronization: calendarSynchronization = {} }
  } = useGet();

  return (
    <GoogleCalendar serviceAccount={serviceAccount} calendarSynchronization={calendarSynchronization} isLoading={isLoading} />
  );
};

export default IntegrationsGoogleCalendarContainer;
