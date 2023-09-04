export const getEnvironmentDisplayedName = (environment = {}) => environment.name ?? environment.details?.cloud_resource_id;
