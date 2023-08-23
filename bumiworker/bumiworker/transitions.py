from bumiworker.bumiworker.consts import TaskState
from bumiworker.bumiworker.tasks import (
    SetStarted, InitializeChecklist, WaitChecklist, CollectCheckResult,
    InitializeArchive, WaitArchive, CheckArchiveResult, InitializeService,
    WaitService, UpdateChecklist, SetSucceededNotifiable, SetFailedNotifiable,
    Process, Cleanup, SetFailed)


TASKS_TRANSITIONS = {
    TaskState.CREATED: SetStarted,
    TaskState.STARTED: InitializeChecklist,
    TaskState.INITIALIZED_CHECKLIST: WaitChecklist,
    TaskState.WAITED_CHECKLIST: CollectCheckResult,
    TaskState.COLLECTED_CHECK_RESULT: InitializeArchive,
    TaskState.INITIALIZED_ARCHIVE: WaitArchive,
    TaskState.WAITED_ARCHIVE: CheckArchiveResult,
    TaskState.CHECKED_ARCHIVE_RESULT: InitializeService,
    TaskState.INITIALIZED_SERVICE: WaitService,
    TaskState.WAITED_SERVICE: UpdateChecklist,
    TaskState.UPDATED_CHECKLIST: SetSucceededNotifiable,
    TaskState.ERROR: SetFailedNotifiable
}

GROUP_TASKS_TRANSITIONS = {
    TaskState.CREATED: SetStarted,
    TaskState.STARTED: Process,
    TaskState.PROCESSED: Cleanup,
    TaskState.ERROR: SetFailed
}
