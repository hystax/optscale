const stringWithDefault =
  (defaultValue: string = "") =>
  (value: string | undefined) =>
    value ?? defaultValue;

const oneOf =
  <const T extends readonly string[]>(validValues: T, defaultValue: T[number]) =>
  (value: string | undefined): T[number] => {
    if (validValues.includes(value as T[number])) {
      return value as T[number];
    }
    return defaultValue;
  };

const envSchema = Object.freeze({
  VITE_APOLLO_HTTP_BASE: stringWithDefault(),
  VITE_APOLLO_WS_BASE: stringWithDefault(),
  VITE_GOOGLE_OAUTH_CLIENT_ID: stringWithDefault(),
  VITE_ON_INITIALIZE_ORGANIZATION_SETUP_MODE: oneOf(["automatic", "invite-only"], "automatic"),
  VITE_GOOGLE_MAP_API_KEY: stringWithDefault(),
  VITE_GANALYTICS_ID: stringWithDefault(),
  VITE_BASE_URL: stringWithDefault(),
  VITE_FINOPS_IN_PRACTICE_PORTAL_OVERVIEW: oneOf(["enabled", "disabled"], "disabled"),
  VITE_HOTJAR_ID: stringWithDefault(),
  VITE_MICROSOFT_OAUTH_CLIENT_ID: stringWithDefault(),
  VITE_BILLING_INTEGRATION: oneOf(["enabled", "disabled"], "disabled"),
});

type EnvKeys = keyof typeof envSchema;

type EnvVariables = {
  [K in EnvKeys]?: string;
};

const envProvider = (window.optscale || import.meta.env) as EnvVariables;

export const getEnvironmentVariable = <K extends EnvKeys>(key: K): ReturnType<(typeof envSchema)[K]> => {
  const value = envProvider[key];
  return envSchema[key](value) as ReturnType<(typeof envSchema)[K]>;
};
