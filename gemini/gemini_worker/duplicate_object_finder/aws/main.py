import os
import logging
import botocore
from datetime import datetime
from collections import defaultdict

from gemini.gemini_worker.duplicate_object_finder.aws.object_info import ObjectInfo
from gemini.gemini_worker.duplicate_object_finder.aws.stats import Stats
from gemini.gemini_worker.duplicate_object_finder.aws.object_enumerator import (
    DefaultAWSClientFactory, AWSObjectEnumerator, )
from gemini.gemini_worker.duplicate_object_finder.aws.sqlite_cache import (
    SqliteCache,
)
from gemini.gemini_worker.duplicate_object_finder.aws.duplicate_finder import (
    DuplicateObjectFinder,
)
from gemini.gemini_worker.utils import random_string


LOG = logging.getLogger(__name__)

CACHE_PATH = "gemini_worker/cache"


def find_duplicates(
    data: list[tuple], filters: dict, preserve_temp_db: bool = False
) -> list[ObjectInfo]:
    start_time = datetime.now()
    LOG.info("Started at %s", start_time)

    stats = Stats()

    if stats.buckets is None:
        stats.buckets = defaultdict(
            lambda: {
                "total_objects": 0,
                "filtered_objects": 0,
                "size": 0,
                "objects_with_duplicates": 0,
                "objects_with_duplicates_size": 0,
            },
        )

    cache_filename = os.path.join(CACHE_PATH, f"{random_string()}.sqlite")
    LOG.info(f"Cache filename is {cache_filename}")
    cache = SqliteCache(cache_filename, stats)

    enumerators = []

    for config, buckets in data:
        client_factory = DefaultAWSClientFactory(
            access_key_id=config.get("access_key_id"),
            secret_access_key=config.get("secret_access_key"),
        )
        enumerator = AWSObjectEnumerator(buckets, stats, client_factory)
        enumerators.append(enumerator)

    result = []

    try:
        dof = DuplicateObjectFinder(enumerators, cache, stats)
        min_size = filters.get("min_size")
        # Both None and 0 should be "invalid" to exclude empty folders
        if not min_size:
            min_size = 1

        # Save collected buckets across all cloud accounts into sqlite db cache
        dof.do_cache(min_size)

        result = dof.find_duplicates()
    except botocore.exceptions.ClientError as exc:
        LOG.exception(
            f"botocore ClientError occured when trying to find duplicates: {exc}"
        )
        raise exc
    except Exception as exс:
        LOG.exception(f"Could not find duplicates: {exс}")
    finally:
        cache.close()
        if not preserve_temp_db:
            os.remove(cache_filename)

    end_time = datetime.now()

    total_time = end_time - start_time
    LOG.info(f"Total time: {total_time}")
    LOG.info(f"Finished at {end_time}")

    return result, stats
