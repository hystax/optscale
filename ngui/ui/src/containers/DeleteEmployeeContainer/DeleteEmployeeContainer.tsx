import { useDispatch } from "react-redux";
import { deleteEmployee } from "api";
import { GET_CURRENT_EMPLOYEE, DELETE_EMPLOYEE } from "api/restapi/actionTypes";
import DeleteEmployeeForm from "components/DeleteEmployeeForm";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { MANAGER, SCOPE_TYPES } from "utils/constants";

const getOrganizationManagers = (employees) =>
  employees.filter((employee) => {
    const isOrganizationManager = employee.assignments.some(
      (el) => el.purpose === MANAGER && el.assignment_resource_type === SCOPE_TYPES.ORGANIZATION
    );
    return isOrganizationManager;
  });

const getOrganizationManagersWhoSuitableForAssignment = (organizationManagers, deletedEmployeeId) =>
  organizationManagers
    .filter((employee) => {
      if (employee.id === deletedEmployeeId) {
        return false;
      }
      return true;
    })
    .map((el) => ({
      value: el.id,
      name: el.name
    }));

const DeleteEmployeeContainer = ({ employees, closeSideModal, entityToBeDeleted }) => {
  const { apiData: { currentEmployee: { id: currentEmployeeId } = {} } = {} } = useApiData(GET_CURRENT_EMPLOYEE);
  const { isLoading } = useApiState(DELETE_EMPLOYEE);
  const dispatch = useDispatch();
  const { name } = useOrganizationInfo();

  const organizationManagers = getOrganizationManagers(employees);

  const onSubmit = (formData) => {
    dispatch((_, getState) => {
      dispatch(deleteEmployee(entityToBeDeleted.employeeId, { newOwnerId: formData.organizationManagerId })).then(() => {
        if (!isError(DELETE_EMPLOYEE, getState())) {
          closeSideModal();
        }
      });
    });
  };

  return (
    <DeleteEmployeeForm
      organizationName={name}
      organizationManagersWhoSuitableForAssignment={getOrganizationManagersWhoSuitableForAssignment(
        organizationManagers,
        entityToBeDeleted.employeeId
      )}
      isOnlyOneOrganizationManager={organizationManagers.length === 1}
      isDeletingMyself={currentEmployeeId === entityToBeDeleted.employeeId}
      onSubmit={onSubmit}
      entityToBeDeleted={entityToBeDeleted}
      closeSideModal={closeSideModal}
      isLoading={isLoading}
    />
  );
};

export default DeleteEmployeeContainer;
