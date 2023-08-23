export const getEnvironmentVariable = (key) => window.optscale?.[key] || process.env[key];
