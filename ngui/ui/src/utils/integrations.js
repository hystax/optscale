import { getEnvironmentVariable } from "./env";

export const microsoftOAuthConfiguration = {
  auth: {
    clientId: getEnvironmentVariable("REACT_APP_MICROSOFT_OAUTH_CLIENT_ID")
  }
};
