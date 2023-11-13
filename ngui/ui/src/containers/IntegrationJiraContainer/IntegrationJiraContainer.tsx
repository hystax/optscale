import { GET_CURRENT_EMPLOYEE } from "api/restapi/actionTypes";
import Jira from "components/Integrations/Jira";
import { useApiData } from "hooks/useApiData";
import EmployeesService from "services/EmployeesService";
import JiraOrganizationStatusService from "services/JiraOrganizationStatusService";

const IntegrationJiraContainer = () => {
  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();

  const { useGet: useGetJiraOrganizationStatus } = JiraOrganizationStatusService();
  const { isLoading: isGetJiraOrganizationStatusLoading, connectedTenants } = useGetJiraOrganizationStatus();

  const { apiData: { currentEmployee: { jira_connected: isCurrentEmployeeConnectedToJira = false } = {} } = {} } =
    useApiData(GET_CURRENT_EMPLOYEE);

  return (
    <Jira
      totalEmployees={employees.length}
      connectedEmployees={employees.filter((el) => el.jira_connected).length}
      connectedWorkspaces={connectedTenants}
      isCurrentEmployeeConnectedToJira={isCurrentEmployeeConnectedToJira}
      isLoadingProps={{ isGetEmployeesLoading, isGetJiraOrganizationStatusLoading }}
    />
  );
};

export default IntegrationJiraContainer;
