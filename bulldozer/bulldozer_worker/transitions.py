from tasks import (
    TaskState,
    StartInfra,
    WaitArcee,
    WaitRun,
    Stop,
    SetSucceeded,
    SetFailed,
)


TRANSITIONS = {
    TaskState.STARTING_PREPARING: StartInfra,
    TaskState.WAITING_ARCEE: WaitArcee,
    TaskState.DESTROYING_SCHEDULED: Stop,
    TaskState.DESTROYED: SetSucceeded,
    TaskState.STARTED: WaitRun,
    TaskState.ERROR: SetFailed,
}
