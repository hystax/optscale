import { UPDATE_ORGANIZATION_TOP_ALERT } from "./actionTypes";

export const updateOrganizationTopAlert = (organizationId, alert) => ({
  type: UPDATE_ORGANIZATION_TOP_ALERT,
  payload: {
    organizationId,
    alert
  }
});
