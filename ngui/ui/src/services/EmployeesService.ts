import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getEmployees } from "api";
import { GET_EMPLOYEES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { employees = [] }
  } = useApiData(GET_EMPLOYEES);

  const { isLoading, shouldInvoke } = useApiState(GET_EMPLOYEES, {
    organizationId,
    roles: true
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getEmployees(organizationId, true));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, employees };
};

function EmployeesService() {
  return { useGet };
}

export default EmployeesService;
