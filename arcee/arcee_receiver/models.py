import uuid
from enum import Enum
from datetime import datetime, timezone
from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, Field, NonNegativeInt,
    model_validator)
from typing import List, Optional, Union
from typing_extensions import Annotated


class ArceeState:
    STARTED = 1
    FINISHED = 2
    ERROR = 3
    ABORTED = 4


class BaseClass(BaseModel):
    model_config = ConfigDict(extra='forbid')


id_ = Field(default_factory=lambda: str(uuid.uuid4()), alias='_id')
now = Field(
        default_factory=lambda: int(datetime.now(tz=timezone.utc).timestamp()))
now_ms = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).timestamp())
date_start = Field(
        default_factory=lambda: int(datetime.now(tz=timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0).timestamp()),
        alias='_created_at_dt')


class ConsolePostIn(BaseClass):
    output: str
    error: str


class Console(ConsolePostIn):
    id: str = id_
    run_id: str


class DatasetPatchIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = []
    timespan_from: Optional[int] = None
    timespan_to: Optional[int] = None

    @model_validator(mode='after')
    def set_labels(self):
        if self.labels:
            self.labels = list(set(self.labels))
        return self


class DatasetPostIn(DatasetPatchIn):
    path: str

    @model_validator(mode='after')
    def set_name(self):
        if not self.name:
            self.name = self.path
        return self


class Dataset(DatasetPostIn):
    id: str = id_
    token: str
    created_at: int = now
    deleted_at: int = 0


class RunPatchIn(BaseClass):
    finish: Optional[bool] = None
    tags: Optional[dict] = {}
    hyperparameters: Optional[dict] = {}
    reason: Optional[str] = None
    state: Optional[int] = None
    runset_id: Optional[str] = None
    runset_name: Optional[str] = None


class Git(BaseClass):
    remote: str
    branch: str
    commit_id: str
    status: str


class RunPostIn(BaseClass):
    name: str
    imports: list[str] = []
    git: Optional[Git] = None
    command: str


class Run(RunPostIn, RunPatchIn):
    id: str = id_
    task_id: str
    start: int = now
    number: int
    deleted_at: int = 0
    data: dict = {}
    executors: list = []
    dataset_id: Optional[str] = None
    state: int = ArceeState.STARTED
    finish: Optional[int] = None


class TaskPatchIn(BaseClass):
    metrics: Optional[List[str]] = []
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class LeaderboardFilter(BaseClass):
    id: str = Field(description='metric id to filter by')
    min: Optional[float] = None
    max: Optional[float] = None

    @model_validator(mode='after')
    def validate_min_max(self):
        if (self.min is None and self.max is None or
                (self.min is not None and self.max is not None and
                 self.min > self.max)):
            raise ValueError('Invalid min/max filter values')
        return self


class LeaderboardTemplatePostIn(BaseClass):
    primary_metric: str
    group_by_hp: bool
    grouping_tags: List[str] = []
    other_metrics: List[str] = []
    filters: List[LeaderboardFilter] = []
    metrics: List[str] = Field(
        [],
        description='list of metrics from primary_metric and other_metrics',
        exclude=True)
    dataset_coverage_rules: Optional[dict] = {}

    @model_validator(mode='after')
    def validate_filters_values(self):
        metrics_ids = self.other_metrics + [self.primary_metric]
        filters_ids = [x.id for x in self.filters]
        if any(x not in metrics_ids for x in filters_ids):
            raise ValueError('Invalid filters')
        return self

    @model_validator(mode='after')
    def set_metrics(self):
        self.metrics = list(set(self.other_metrics + [self.primary_metric]))
        return self

    @model_validator(mode='after')
    def validate_dataset_coverage_rules(self):
        if self.dataset_coverage_rules and not all(
                isinstance(x, int) and 0 < x <= 100 for x in
                self.dataset_coverage_rules.values()):
            raise ValueError('value of dataset_coverage_rules should be int '
                             'between 1 and 100')


class LeaderboardTemplatePatchIn(LeaderboardTemplatePostIn):
    primary_metric: Optional[str] = None
    group_by_hp: Optional[bool] = None

    @model_validator(mode='after')
    def set_metrics(self):
        self.metrics = list(set(self.other_metrics))
        if self.primary_metric:
            self.metrics = list(set(self.metrics + [self.primary_metric]))
        return self

    @model_validator(mode='after')
    def validate_filters_values(self):
        return self


class LeaderboardTemplate(LeaderboardTemplatePostIn):
    id: str = id_
    task_id: str
    token: str
    created_at: int = now
    deleted_at: int = 0

    class Config:
        allow_population_by_field_name = True


class LeaderboardPatchIn(LeaderboardTemplatePatchIn):
    dataset_ids: Optional[list] = []
    name: Optional[str] = None

    @staticmethod
    def remove_dup_ds_ids(kwargs):
        ds_ids = kwargs.get("dataset_ids")
        if ds_ids:
            kwargs["dataset_ids"] = list(set(ds_ids))


class LeaderboardPostIn(LeaderboardPatchIn):
    pass


class Leaderboard(LeaderboardPostIn):
    id: str = id_
    token: str
    leaderboard_template_id: str
    created_at: int = now
    deleted_at: int = 0


class PlatformType(str, Enum):
    alibaba = "alibaba"
    aws = "aws"
    azure = "azure"
    gcp = "gcp"
    unknown = "unknown"


class InstanceLifeCycle(str, Enum):
    OnDemand = "OnDemand"
    Preemptible = "Preemptible"
    Spot = "Spot"
    Unknown = "Unknown"


class PlatformPostIn(BaseClass):
    platform_type: PlatformType
    instance_id: str
    account_id: str
    local_ip: str
    public_ip: str
    instance_lc: InstanceLifeCycle
    instance_type: str
    instance_region: str
    availability_zone: str


def filter_strings(stats: dict) -> dict:
    return {k: v for k, v in stats.items() if isinstance(v, (int, float))}


StatsData = Annotated[
    dict[str, Union[int, float]], BeforeValidator(filter_strings)]


class StatsPostIn(BaseClass):
    project: str
    run: str
    data: StatsData
    platform: PlatformPostIn


class Platform(PlatformPostIn):
    id: str = id_


class Log(BaseClass):
    project: str
    run_id: str
    data: StatsData
    instance_id: Optional[str]
    id: str = id_
    timestamp: float = now_ms


class ModelPatchIn(BaseClass):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[dict] = {}


class ModelPostIn(ModelPatchIn):
    key: str

    @model_validator(mode='after')
    def set_name(self):
        if not self.name:
            self.name = self.key
        return self


class Model(ModelPostIn):
    id: str = id_
    token: str
    created_at: int = now


class ModelVersionIn(BaseClass):
    path: Optional[str] = None
    aliases: Optional[List[str]] = []
    version: Optional[str] = None
    tags: Optional[dict] = {}

    @model_validator(mode='after')
    def set_aliases(self):
        if self.aliases:
            self.aliases = list(set(self.aliases))
        return self


class ModelVersion(ModelVersionIn):
    id: str = id_
    deleted_at: int = 0
    run_id: str
    model_id: str
    created_at: int = now


class MetricFunc(str, Enum):
    avg = "avg"
    last = "last"
    max = "max"
    sum = "sum"


class MetricTendency(str, Enum):
    less = "less"
    more = "more"


class MetricPostIn(BaseClass):
    name: Optional[str] = None
    key: str
    target_value: float
    func: MetricFunc
    tendency: MetricTendency


class MetricPatchIn(MetricPostIn):
    key: Optional[str] = None
    target_value: Optional[float] = None
    func: Optional[MetricFunc] = None
    tendency: Optional[MetricTendency] = None


class Metric(MetricPatchIn):
    id: str = id_
    token: str


class ArtifactPatchIn(BaseClass):
    path: str = None
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[dict] = {}


class ArtifactPostIn(ArtifactPatchIn):
    run_id: str
    path: str

    @model_validator(mode='after')
    def set_name(self):
        if not self.name:
            self.name = self.path
        return self


class Artifact(ArtifactPostIn):
    id: str = id_
    token: str
    created_at: int = now
    created_at_dt: int = date_start


timestamp = Field(None, ge=0, le=2**31-1)
max_mongo_int = Field(0, ge=0, le=2**63-1)


class ArtifactSearchParams(BaseModel):
    created_at_lt: Optional[NonNegativeInt] = timestamp
    created_at_gt: Optional[NonNegativeInt] = timestamp
    limit: Optional[NonNegativeInt] = max_mongo_int
    start_from: Optional[NonNegativeInt] = max_mongo_int
    run_id: Optional[Union[list, str]] = []
    task_id: Optional[Union[list, str]] = []
    text_like: Optional[str] = None

    @model_validator(mode='before')
    def convert_to_expected_types(self):
        """
        Converts a dict of request.args passed as query parameters to a dict
        suitable for further model validation.

        Example:
          request.args: {"limit": ["1"], "text_like": ["test"]}
          return: {"limit": "1", "text_like": "test"}
        """
        numeric_fields = ['created_at_lt', 'created_at_gt',
                          'limit', 'start_from']
        for k, v in self.items():
            if isinstance(v, list) and len(v) == 1:
                v = v[0]
                self[k] = v
            if k in numeric_fields:
                try:
                    self[k] = int(v)
                except (TypeError, ValueError):
                    continue
        return self

    @model_validator(mode='after')
    def validate_run_id(self):
        if isinstance(self.run_id, str):
            self.run_id = [self.run_id]
        return self

    @model_validator(mode='after')
    def validate_created_at(self):
        if (self.created_at_gt is not None and self.created_at_lt is not None
                and self.created_at_lt <= self.created_at_gt):
            raise ValueError('Invalid created_at filter values')
        return self

    @model_validator(mode='after')
    def validate_task_id(self):
        if isinstance(self.task_id, str):
            self.task_id = [self.task_id]
        return self
