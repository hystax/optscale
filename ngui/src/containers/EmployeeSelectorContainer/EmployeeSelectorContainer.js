import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { getEmployees } from "api";
import { GET_EMPLOYEES } from "api/restapi/actionTypes";
import EmployeeSelector from "components/EmployeeSelector";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { setEmployeeId } from "reducers/resources/actionCreators";

const EmployeeSelectorContainer = ({ splitGroup, excludeMyself, error, helperText, dataTestId }) => {
  const { organizationId } = useOrganizationInfo();

  const resourcesState = useSelector((state) => state.resources);
  const { [splitGroup]: { employeeId = "" } = {} } = resourcesState;

  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_EMPLOYEES, { organizationId, roles: false });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getEmployees(organizationId, false, excludeMyself));
    }
  }, [shouldInvoke, dispatch, organizationId, excludeMyself]);

  const onChange = (newEmployeeId) => {
    dispatch(setEmployeeId(newEmployeeId, splitGroup));
  };

  const {
    apiData: { employees = [] }
  } = useApiData(GET_EMPLOYEES);

  return (
    <EmployeeSelector
      error={error}
      helperText={helperText}
      employees={employees}
      selected={employeeId}
      onChange={onChange}
      isLoading={isLoading}
      dataTestId={dataTestId}
    />
  );
};

EmployeeSelectorContainer.propTypes = {
  splitGroup: PropTypes.string.isRequired,
  excludeMyself: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default EmployeeSelectorContainer;
