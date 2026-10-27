import { MANAGER, SCOPE_TYPES } from "./constants";

export const isOrganizationManager = (employee) =>
  employee.assignments.some(
    (assignment) => assignment.purpose === MANAGER && assignment.assignment_resource_type === SCOPE_TYPES.ORGANIZATION
  );

export const isPoolManager = (employee, poolId) => {
  const poolAssignment = employee.assignments.find(
    (assignment) => assignment.assignment_resource_type === SCOPE_TYPES.POOL && assignment.assignment_resource_id === poolId
  );
  return poolAssignment && poolAssignment.purpose === MANAGER;
};

export const getOrganizationManagers = (employees) => employees.filter(isOrganizationManager);

export const getOrganizationManagersWhoSuitableForAssignment = (organizationManagers, deletedEmployeeId) =>
  organizationManagers
    .filter((employee) => {
      if (employee.id === deletedEmployeeId) {
        return false;
      }
      return true;
    })
    .map((el) => ({
      value: el.id,
      name: el.name,
    }));
