import macaroon from "utils/macaroons";
import { SET_ALLOWED_ACTIONS, SET_TOKEN, SET_USER } from "./actionTypes";

export const AUTH = "auth";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_TOKEN: {
      const { token, user_id: userId, user_email: userEmail, isTemporary } = action.payload;

      const caveats = macaroon.processCaveats(macaroon.deserialize(token).getCaveats());

      return {
        ...state,
        [action.label]: {
          userId,
          userEmail,
          /**
           * The use of a temporary token is a security measure to ensure that users update their passwords before gaining full access to the application.
           * This prevents users from accessing other parts of the application until their password has been successfully changed.
           */
          [isTemporary ? "temporaryToken" : "token"]: token,
          ...caveats
        }
      };
    }
    case SET_USER:
      return {
        ...state,
        [action.label]: {
          name: action.payload.display_name,
          email: action.payload.email
        }
      };
    case SET_ALLOWED_ACTIONS: {
      return {
        ...state,
        [action.label]: {
          allowedActions: {
            ...state[action.label]?.allowedActions,
            ...action.payload.allowed_actions
          }
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
