from gemini.gemini_worker.duplicate_object_finder.aws.object_info import (
    ObjectInfo)
from gemini.gemini_worker.duplicate_object_finder.aws.main import find_duplicates


# TODO: At this point only AWS S3 is supported. When it is clear what can
# be extracted in a base/generic class and logic, refactor to classes
class Factory:
    @staticmethod
    def get(
        data: list[tuple],
        filters: dict,
        type_: str = "aws_cnr",
    ) -> list[ObjectInfo]:
        if type_ == "aws_cnr":
            return find_duplicates(data, filters)

        raise Exception(f"Unknown type: {type_}")
