import { SET_POOL_ID, SET_OWNER_ID, SET_EMPLOYEE_ID, SET_ACTIVE_TAB, RESET_RESOURCES } from "./actionTypes";

export const setPoolId = (poolId, splitGroup) => ({
  type: SET_POOL_ID,
  poolId,
  splitGroup
});

export const setOwnerId = (ownerId, splitGroup) => ({
  type: SET_OWNER_ID,
  ownerId,
  splitGroup
});

export const setEmployeeId = (employeeId, splitGroup) => ({
  type: SET_EMPLOYEE_ID,
  employeeId,
  splitGroup
});

export const setActiveTab = (tabIndex, splitGroup) => ({
  type: SET_ACTIVE_TAB,
  tabIndex,
  splitGroup
});

export const resetResources = () => ({
  type: RESET_RESOURCES
});
