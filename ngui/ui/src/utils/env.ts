export const getEnvironmentVariable = (key) => window.optscale?.[key] || import.meta.env[key];
