import { getEnvironmentVariable } from "./env";

export const microsoftOAuthConfiguration = {
  auth: {
    clientId: getEnvironmentVariable("VITE_MICROSOFT_OAUTH_CLIENT_ID")
  }
};
