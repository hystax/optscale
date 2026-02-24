import UserEmailNotificationSettings from "components/UserEmailNotificationSettings";
import { useEmployeeEmailsQuery } from "graphql/__generated__/hooks/restapi";
import { useCurrentEmployee } from "hooks/coreData/useCurrentEmployee";

const UserEmailNotificationSettingsContainer = () => {
  const currentEmployee = useCurrentEmployee();

  const { loading, data } = useEmployeeEmailsQuery({
    variables: {
      employeeId: currentEmployee.id,
    },
  });

  return <UserEmailNotificationSettings employeeEmails={data?.employeeEmails ?? []} isLoading={loading} />;
};

export default UserEmailNotificationSettingsContainer;
