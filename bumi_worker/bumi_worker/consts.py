class TaskState(object):
    CREATED = 'created'
    STARTED = 'started'
    INITIALIZED_CHECKLIST = 'initialized_checklist'
    WAITED_CHECKLIST = 'waited_checklist'
    COLLECTED_CHECK_RESULT = 'collected_check_result'
    INITIALIZED_ARCHIVE = 'initialized_archive'
    WAITED_ARCHIVE = 'waited_archive'
    CHECKED_ARCHIVE_RESULT = 'check_archive_result'
    INITIALIZED_SERVICE = 'initialized_service'
    WAITED_SERVICE = 'waited_service'
    UPDATED_CHECKLIST = 'updated_checklist'
    PROCESSED = 'processed'
    COMPLETED = 'completed'
    ERROR = 'error'


class ArchiveReason(object):
    OPTIONS_CHANGED = 'options_changed'
    CLOUD_ACCOUNT_DELETED = 'cloud_account_deleted'
    RECOMMENDATION_APPLIED = 'recommendation_applied'
    RECOMMENDATION_IRRELEVANT = 'recommendation_irrelevant'
    RESOURCE_DELETED = 'resource_deleted'
    FAILED_DEPENDENCY = 'failed_dependency'
