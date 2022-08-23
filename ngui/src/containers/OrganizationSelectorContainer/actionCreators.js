import { SET_SCOPE_ID } from "./actionTypes";

export const setScopeId = (organizationId) => ({
  type: SET_SCOPE_ID,
  organizationId
});
