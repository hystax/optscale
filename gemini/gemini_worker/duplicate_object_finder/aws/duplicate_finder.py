import logging
from gemini.gemini_worker.duplicate_object_finder.aws.object_info import ObjectInfo

LOG = logging.getLogger(__name__)


class DuplicateObjectFinder:
    def __init__(self, object_enumerators, cache, stats):
        self._object_enumerators = object_enumerators
        self._cache = cache
        self._stats = stats

    @staticmethod
    def _filter_out_by_size(
            lst: list[ObjectInfo],
            size: int) -> list[ObjectInfo]:
        return [item for item in filter(lambda x: x.size >= size, lst)]

    @staticmethod
    def _calculate_dup_size(lst: list[ObjectInfo]) -> int:
        """
        :param lst: sorted by tag list of ObjectInfo
        :return: sum of size of all duplicate items except one in each group of duplicates
        """
        res = 0
        if len(lst) > 0:
            cur_item = lst[0]
            for item in lst[1:]:
                if item.tag == cur_item.tag:
                    res += item.size
                else:
                    cur_item = item
        return res

    def do_cache(self, min_size) -> None:
        try:
            for object_enumerator in self._object_enumerators:
                for object_info_list in object_enumerator.enumerate():
                    bucket = object_info_list[0].bucket
                    total_objects = len(object_info_list)
                    self._stats.total_objects += total_objects

                    object_info_list = self._filter_out_by_size(
                        object_info_list, min_size
                    )
                    filtered_objects = len(object_info_list)

                    self._stats.filtered_objects += filtered_objects

                    size = sum([item.size for item in object_info_list])
                    self._stats.total_size += size

                    self._stats.buckets[bucket] = {
                        "total_objects": self._stats.buckets[bucket]["total_objects"] +
                        total_objects,
                        "filtered_objects": self._stats.buckets[bucket]["filtered_objects"] +
                        filtered_objects,
                        "size": self._stats.buckets[bucket]["size"] +
                        size,
                    }

                    self._cache.add(object_info_list)
        except Exception as exc:
            LOG.exception(f"DOF: Could not cache objects: {exc}")
            raise exc

    def find_duplicates(self) -> list[ObjectInfo]:
        try:
            res = sorted(self._cache.get_duplicates(), key=lambda x: x.tag)
            self._stats.duplicates_size += self._calculate_dup_size(res)
            self._stats.duplicated_objects += len(res)
            return res
        except Exception as exc:
            LOG.exception(f"DOF: Could not find duplicates: {exc}")
            raise exc
