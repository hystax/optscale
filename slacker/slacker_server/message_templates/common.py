def get_resource_type_location(resource_data):
    r_type = resource_data['resource_type']

    location = resource_data.get('cloud_account_name')
    if not location:
        location = "Cluster" if resource_data.get('cluster_type_id') else None

    return f"{r_type}{f' ({location})' if location else ''}"
