import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getOrganizationExpenses } from "api";
import { GET_ORGANIZATION_EXPENSES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetOrganizationExpenses = () => {
  const { organizationId } = useOrganizationInfo();

  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_EXPENSES, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationExpenses(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  const { apiData: data } = useApiData(GET_ORGANIZATION_EXPENSES);

  return {
    isLoading,
    data
  };
};

function ExpensesService() {
  return { useGetOrganizationExpenses };
}

export default ExpensesService;
