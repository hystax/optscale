import { API_START, API_END, API_SUCCESS, API_ERROR, RESET_TTL } from "./actionTypes";
import { SUCCESS_HANDLER_TYPE_ALERT } from "./constants";

export const API = "api";
export const LATEST_SUCCESS_HANDLED_LABEL = "latestSuccessHandledLabel";

const reducer = (state = { latestErrorLabel: "", [LATEST_SUCCESS_HANDLED_LABEL]: "" }, action) => {
  switch (action.type) {
    case API_START: {
      return {
        ...state,
        [action.payload.label]: {
          ...state[action.payload.label],
          isLoading: true,
          hash: action.payload.hash,
          entityId: action.payload.entityId
        }
      };
    }
    case API_END:
      return {
        ...state,
        [action.payload]: {
          ...state[action.payload],
          isLoading: false
        }
      };
    case API_SUCCESS: {
      const status = state[action.payload.label] || {};

      const newState = {
        ...state,
        [action.payload.label]: {
          ...status,
          timestamp: new Date().getTime() + action.payload.ttl,
          status: {
            ...status.status,
            isError: false,
            successHandlerType: action.payload.successHandlerType,
            response: {
              data: {
                success: {
                  statusText: action.payload.response.statusText,
                  code: action.payload.code,
                  messageParams: action.payload.messageParams,
                  reason: action.payload.label,
                  alertSeverity: action.payload.alertSeverity
                }
              }
            }
          }
        }
      };

      if (action.payload.successHandlerType === SUCCESS_HANDLER_TYPE_ALERT) {
        const includeLatestSuccessHandledLabel = () => {
          newState[LATEST_SUCCESS_HANDLED_LABEL] = action.payload.label;
        };
        includeLatestSuccessHandledLabel();
      }

      return newState;
    }
    case API_ERROR: {
      const status = state[action.payload.label] || {};
      const response = {
        ...action.payload.response,
        config: {
          url: action.payload.response.config.url,
          params: { ...action.payload.response.config.params }
        }
      };
      return {
        ...state,
        latestErrorLabel: action.payload.label,
        [action.payload.label]: {
          ...status,
          status: {
            ...status.status,
            isError: true,
            errorHandlerType: action.payload.errorHandlerType,
            response
          }
        }
      };
    }
    case RESET_TTL: {
      return {
        ...state,
        [action.label]: {
          ...state[action.label],
          timestamp: 0
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
