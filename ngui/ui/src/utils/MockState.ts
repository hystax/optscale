import { GET_POOL_ALLOWED_ACTIONS, GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";

export function MockState(defaultState = {}) {
  let state = defaultState;

  const mockPoolPermissions = (poolId, allowedActions) => {
    state = {
      ...state,
      auth: {
        // copy entire auth state
        ...state.auth,
        [GET_POOL_ALLOWED_ACTIONS]: {
          allowedActions: {
            // copy allowedActions object if exists
            ...(state.auth?.[GET_POOL_ALLOWED_ACTIONS]?.allowedActions ?? {}),
            // merge existed permissions (if they exist) with new permissions
            [poolId]: Array.from(
              new Set([...(state.auth?.[GET_POOL_ALLOWED_ACTIONS]?.allowedActions?.[poolId] ?? []), ...allowedActions])
            ),
          },
        },
      },
    };
  };

  const mockResourcePermissions = (resourceId, allowedActions) => {
    state = {
      ...state,
      auth: {
        // copy entire auth state
        ...state.auth,
        [GET_RESOURCE_ALLOWED_ACTIONS]: {
          allowedActions: {
            // copy allowedActions object if exists
            ...(state.auth?.[GET_RESOURCE_ALLOWED_ACTIONS]?.allowedActions ?? {}),
            // merge existed permissions (if they exist) with new permissions
            [resourceId]: Array.from(
              new Set([...(state.auth?.[GET_RESOURCE_ALLOWED_ACTIONS]?.allowedActions?.[resourceId] ?? []), ...allowedActions])
            ),
          },
        },
      },
    };
  };

  const mockOrganizationPermissions = (organizationId) => {
    state = {
      ...state,
      // get organization id from state or set a new value
      organizationId: state.organizationId || organizationId,
    };
  };

  const mockRestapi = (payload) => {
    state = {
      ...state,
      restapi: {
        ...state.restapi,
        ...payload,
      },
    };
  };

  return {
    mockPoolPermissions,
    mockOrganizationPermissions,
    mockResourcePermissions,
    mockRestapi,
    get state() {
      return state;
    },
  };
}
