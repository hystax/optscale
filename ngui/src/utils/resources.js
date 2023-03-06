export const getCloudResourceIdentifier = (resource) => resource.cloud_resource_id ?? resource.cloud_resource_hash;

export const getResourceDisplayedName = (resource) => resource.name ?? getCloudResourceIdentifier(resource);
