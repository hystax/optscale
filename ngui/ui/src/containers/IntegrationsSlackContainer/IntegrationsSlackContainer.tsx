import { useQuery } from "@apollo/client";
import { GET_CURRENT_EMPLOYEE } from "api/restapi/actionTypes";
import Slack from "components/Integrations/Slack";
import { GET_INSTALLATION_PATH } from "graphql/api/slacker/queries";
import { useApiData } from "hooks/useApiData";
import EmployeesService from "services/EmployeesService";

const IntegrationsSlackContainer = () => {
  const { useGet: useGetEmployees } = EmployeesService();
  const { isLoading: isGetEmployeesLoading, employees } = useGetEmployees();
  const { apiData: { currentEmployee: { slack_connected: isCurrentEmployeeConnectedToSlack = false } = {} } = {} } =
    useApiData(GET_CURRENT_EMPLOYEE);

  const { loading: isGetSlackInstallationPathLoading, data } = useQuery(GET_INSTALLATION_PATH);

  return (
    <Slack
      totalEmployees={employees.length}
      connectedEmployees={employees.filter((el) => el.slack_connected).length}
      isCurrentEmployeeConnectedToSlack={isCurrentEmployeeConnectedToSlack}
      slackInstallationPath={data?.url}
      isLoadingProps={{ isGetEmployeesLoading, isGetSlackInstallationPathLoading }}
    />
  );
};

export default IntegrationsSlackContainer;
