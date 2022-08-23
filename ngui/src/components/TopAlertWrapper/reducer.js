import { UPDATE_ORGANIZATION_TOP_ALERT } from "./actionTypes";

export const ALERTS = "alerts";

export const ALERT_TYPE = Object.freeze({
  COMMON_ALERTS: "commonAlerts",
  ORGANIZATION_ALERTS: "organizationAlerts"
});

const updateAlertState = (alerts, newAlertState) =>
  alerts.map((currentAlertState) => {
    if (currentAlertState.id === newAlertState.id) return { ...currentAlertState, ...newAlertState };
    return currentAlertState;
  });

const addAlertState = (alerts, newAlertState) => [...alerts, newAlertState];

const alertExists = (alerts, alert) => alerts.some(({ id }) => id === alert.id);

const reducer = (state = {}, action) => {
  switch (action.type) {
    case UPDATE_ORGANIZATION_TOP_ALERT: {
      const {
        payload: { alert, organizationId }
      } = action;

      const currentOrganizationAlerts = state[organizationId] || [];

      return {
        ...state,
        [organizationId]: alertExists(currentOrganizationAlerts, alert)
          ? updateAlertState(currentOrganizationAlerts, alert)
          : addAlertState(currentOrganizationAlerts, alert)
      };
    }
    default:
      return state;
  }
};

export default reducer;
