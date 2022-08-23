from insider_worker.processors.azure import AzurePriceProcessor

PROCESSOR_TYPES = {
    'azure_cnr': AzurePriceProcessor,
}


def get_processor_class(cloud_type):
    if cloud_type not in PROCESSOR_TYPES:
        raise ValueError('Cloud {} is not supported'.format(cloud_type))
    return PROCESSOR_TYPES[cloud_type]
