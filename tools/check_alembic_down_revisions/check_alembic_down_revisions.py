#!/usr/bin/env python

import argparse
import os
import re

DOWN_REVISION_PATTERN = 'down_revision = .*'


class AlembicRevisionChecker:
    def __init__(self, alembic_version_path, ignore_ids):
        self.alembic_version_path = alembic_version_path
        # IGNOR this revisions; TRY to avoid of new
        # This need to pass error of down revisions in rest_api
        self.ignore_ids = ignore_ids

    def have_duplicate(self, file_revision, array_files_revisions):
        ignored_strings = [
            "down_revision = '%s'" % x for x in self.ignore_ids]
        if file_revision["down_revision"] in ignored_strings:
            return False
        for r in array_files_revisions:
            if r["file"] == file_revision["file"]:
                continue
            if r["down_revision"] == file_revision["down_revision"]:
                return True

        return False

    def check_down_revisions(self):
        files = [os.path.join(self.alembic_version_path, f)
                 for f in os.listdir(self.alembic_version_path)
                 if os.path.isfile(os.path.join(self.alembic_version_path, f))]
        array_files_revisions = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                content_of_file = f.read()
                down_revision = re.search(
                    DOWN_REVISION_PATTERN, content_of_file).group()
                array_files_revisions.append(
                    {"file": file, "down_revision": down_revision})

        duplicates_file_revisions = [
            f for f in array_files_revisions
            if self.have_duplicate(f, array_files_revisions)]
        assert len(duplicates_file_revisions) == 0, \
            "Found duplicates down revisions: %s" % duplicates_file_revisions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alembic revision check')
    parser.add_argument('--alembic_versions_path', help='Result image name',
                        required=True)
    parser.add_argument('--ignore_ids', help='List of revisions ids to ignore',
                        nargs='+', required=False, default=[])
    arguments = parser.parse_args()
    alembic_revision_checker = AlembicRevisionChecker(
        arguments.alembic_versions_path, arguments.ignore_ids)
    alembic_revision_checker.check_down_revisions()
