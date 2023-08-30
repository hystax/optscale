from katara.katara_worker.consts import TaskState
from katara.katara_worker.tasks import (
    SetStarted,
    SetGettingScopes,
    GetScopes,
    SetGettingRecipients,
    GetRecipients,
    SetGeneratingReportData,
    GenerateReportData,
    SetPuttingToHerald,
    PutToHerald
)


TASKS_TRANSITIONS = {
    TaskState.CREATED: SetStarted,
    TaskState.STARTED: SetGettingScopes,
    TaskState.GETTING_SCOPES: GetScopes,
    TaskState.GOT_SCOPES: SetGettingRecipients,
    TaskState.GETTING_RECIPIENTS: GetRecipients,
    TaskState.GOT_RECIPIENTS: SetGeneratingReportData,
    TaskState.GENERATING_DATA: GenerateReportData,
    TaskState.GENERATED_DATA: SetPuttingToHerald,
    TaskState.PUTTING_TO_HERALD: PutToHerald
}
