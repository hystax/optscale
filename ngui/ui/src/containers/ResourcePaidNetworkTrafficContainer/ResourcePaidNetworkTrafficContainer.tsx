import ResourcePaidNetworkTraffic from "components/ResourcePaidNetworkTraffic";
import TrafficExpensesService from "services/TrafficExpensesService";

const ResourcePaidNetworkTrafficContainer = ({ resourceId, startDate, endDate }) => {
  const { useGetTrafficExpenses } = TrafficExpensesService();

  const {
    trafficExpenses: { traffic_expenses: expenses = [] },
    isLoading
  } = useGetTrafficExpenses({ startDate, endDate, resourceId });

  return <ResourcePaidNetworkTraffic trafficExpenses={expenses} isLoading={isLoading} />;
};

export default ResourcePaidNetworkTrafficContainer;
