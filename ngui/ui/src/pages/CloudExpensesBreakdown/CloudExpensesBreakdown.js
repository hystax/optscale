import React from "react";
import { useParams } from "react-router-dom";
import CloudExpensesBreakdownContainer from "containers/CloudExpensesBreakdownContainer";
import { CLOUD_DETAILS } from "utils/constants";

const CloudExpensesBreakdown = () => {
  const { cloudAccountId } = useParams();

  return <CloudExpensesBreakdownContainer type={CLOUD_DETAILS} entityId={cloudAccountId} />;
};

export default CloudExpensesBreakdown;
