import { GET_ORGANIZATION_ALLOWED_ACTIONS, GET_POOL_ALLOWED_ACTIONS, GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";

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
            )
          }
        }
      }
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
            )
          }
        }
      }
    };
  };

  const mockOrganizationPermissions = (organizationId, allowedActions) => {
    state = {
      ...state,
      // get organization id from state or set a new value
      organizationId: state.organizationId || organizationId,
      restapi: {
        // copy entire state
        ...state.restapi,
        [GET_ORGANIZATIONS]: {
          organizations: [
            // copy organizations list if exists
            ...(state.restapi?.[GET_ORGANIZATIONS]?.organizations ?? []),
            // if organization with "organizationId" already exists in the state - do nothing, otherwise add new organization
            ...(state.restapi?.[GET_ORGANIZATIONS]?.organizations.some((organization) => organization.id === organizationId)
              ? []
              : [
                  {
                    id: organizationId
                  }
                ])
          ]
        }
      },
      auth: {
        // copy entire auth state
        ...state.auth,
        [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
          allowedActions: {
            // copy allowedActions object if exists
            ...(state.auth?.[GET_ORGANIZATION_ALLOWED_ACTIONS]?.allowedActions ?? {}),
            // merge existed permissions (if they exist) with new permissions
            [organizationId]: Array.from(
              new Set([
                ...(state.auth?.[GET_ORGANIZATION_ALLOWED_ACTIONS]?.allowedActions?.[organizationId] ?? []),
                ...allowedActions
              ])
            )
          }
        }
      }
    };
  };

  const mockRestapi = (payload) => {
    state = {
      ...state,
      restapi: {
        ...state.restapi,
        ...payload
      }
    };
  };

  return {
    mockPoolPermissions,
    mockOrganizationPermissions,
    mockResourcePermissions,
    mockRestapi,
    get state() {
      return state;
    }
  };
}
