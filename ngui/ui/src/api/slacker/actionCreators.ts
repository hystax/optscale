import { handleSuccess } from "api/actionCreators";
import { ERROR_HANDLER_TYPE_LOCAL } from "api/constants";
import { apiAction, getApiUrl } from "api/utils";
import { CONNECT_SLACK_USER, GET_SLACK_INSTALLATION_PATH, SET_SLACK_INSTALLATION_PATH } from "./actionTypes";

const API_URL = getApiUrl("slacker");

export const connectSlackUser = (secret) =>
  apiAction({
    url: `${API_URL}/connect_slack_user`,
    method: "POST",
    label: CONNECT_SLACK_USER,
    params: {
      secret
    },
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL
  });

export const getSlackInstallationPath = () =>
  apiAction({
    url: `${API_URL}/install_path`,
    method: "GET",
    label: GET_SLACK_INSTALLATION_PATH,
    onSuccess: handleSuccess(SET_SLACK_INSTALLATION_PATH)
  });
