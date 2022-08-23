import React from "react";
import PropTypes from "prop-types";
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

ResourcePaidNetworkTrafficContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  startDate: PropTypes.number.isRequired,
  endDate: PropTypes.number.isRequired
};

export default ResourcePaidNetworkTrafficContainer;
