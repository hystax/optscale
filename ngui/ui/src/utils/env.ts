export const getEnvironmentVariable = (key: string, fallback: string = "") =>
  window.optscale?.[key] || import.meta.env[key] || fallback;
