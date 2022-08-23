import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getDetailedCloudAccounts } from "api";
import { GET_DETAILED_CLOUD_ACCOUNTS, GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import CloudExpenses from "components/CloudExpenses";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const CloudExpensesContainer = ({ needCardAlign = false }) => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_DETAILED_CLOUD_ACCOUNTS, organizationId);

  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDetailedCloudAccounts(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return <CloudExpenses needCardAlign={needCardAlign} isLoading={isLoading} cloudAccounts={cloudAccounts} />;
};

CloudExpensesContainer.propTypes = {
  needCardAlign: PropTypes.bool
};

export default CloudExpensesContainer;
