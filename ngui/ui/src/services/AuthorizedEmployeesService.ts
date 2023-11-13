import { useEffect, useMemo } from "react";
import { useDispatch } from "react-redux";
import { getAuthorizedEmployees } from "api";
import { GET_AUTHORIZED_EMPLOYEES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGet = ({ objectType, objectId, permission }) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { employees = [] }
  } = useApiData(GET_AUTHORIZED_EMPLOYEES);

  const requestParams = useMemo(
    () => ({
      objectType,
      objectId,
      permission
    }),
    [objectType, objectId, permission]
  );

  const { isLoading, shouldInvoke } = useApiState(GET_AUTHORIZED_EMPLOYEES, {
    ...requestParams,
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAuthorizedEmployees(organizationId, requestParams));
    }
  }, [shouldInvoke, dispatch, organizationId, requestParams]);

  return { isGetAuthorizedEmployeesLoading: isLoading, employees };
};

function AuthorizedEmployeesService() {
  return { useGet };
}

export default AuthorizedEmployeesService;
