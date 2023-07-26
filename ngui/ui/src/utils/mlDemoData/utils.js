/* eslint-disable no-underscore-dangle */
import { GOAL_STATUS, ML_MODEL_STATUS, ML_RUN_STATUS } from "utils/constants";
import { getGoalsStatus } from "utils/ml";
import { AWS_DEV, AWS_ML, AWS_QA, dataSources } from "./dataSources";
import { executors } from "./executors";
import { executorsBreakdown } from "./executorsBreakdown";
import { modelRecommendations } from "./modelRecommendations";
import { models } from "./models";
import { isParameterReached } from "./parameters";
import { runBreakdowns } from "./runBreakdown";
import { runs } from "./runs";
import { runsets } from "./runsets";
import { runsetTemplates } from "./runsetTemplates";

const getRun = (runId) => runs.find(({ id }) => id === runId);

const getExecutor = (executorId) => executors.find(({ id }) => id === executorId);

const getModelExecutors = (modelId) => {
  const model = models.find(({ id }) => id === modelId);

  if (!model) return [];

  const modelRuns = model.runs.map(getRun);

  const executorIds = Array.from(new Set(modelRuns.map(({ executor_id: executorId }) => executorId)));

  const modelExecutors = executorIds.map(getExecutor);

  return modelExecutors;
};

const getRunExecutor = (runId) => {
  const run = getRun(runId);

  if (!run) {
    return undefined;
  }

  const executor = getExecutor(run.executor_id);

  if (!executor) {
    return undefined;
  }

  return executor;
};

const getRunExecutors = (runId) => {
  const executor = getRunExecutor(runId);

  if (!executor) {
    return [];
  }
  return [executor];
};

const getRunsetExecutors = (runsIds) => {
  const allRuns = runsIds.map(getRun).filter((run) => run !== undefined);

  const executorIds = Array.from(new Set(allRuns.map(({ executor_id: executorId }) => executorId)));

  return executorIds
    .map(getExecutor)
    .filter((executor) => executor !== undefined)
    .map((datum) => ({
      ...datum,
      cloud_account: datum.resource?.cloud_account,
      cost: datum.resource?.total_cost,
      instance_id: datum.resource?.cloud_resource_id,
      instance_name: datum.resource?.name,
      state: "starting scheduled",
      name: datum.resource?.name,
      instance_size: {
        name: datum.resource?.meta?.flavor,
        type: datum.resource?.meta?.flavor?.split(".")?.[0],
        cloud_type: datum.resource?.cloud_account?.type
      }
    }));
};

const getRunsetTemplates = () =>
  runsetTemplates.map((runsetTemplate) => {
    const templateRunsets = runsetTemplate.runsets
      .map((runsetId) => runsets.find(({ id }) => id === runsetId))
      .filter((runset) => runset !== undefined);

    const lastTemplateRunset = templateRunsets[0] ?? {};

    const lastTemplateRunsetRuns = lastTemplateRunset.runs?.map(getRun) ?? [];

    const runsetRuns = templateRunsets.flatMap((runset) => runset.runs).map(getRun);

    const lastTemplateRunsetCost = lastTemplateRunsetRuns.reduce((expensesSum, { cost = 0 }) => expensesSum + cost, 0);

    return {
      ...runsetTemplate,
      runsets: templateRunsets,
      applications: runsetTemplate.applications
        .map((modelId) => models.find(({ id }) => modelId === id))
        .filter((model) => model !== undefined),
      cloud_accounts: [AWS_ML, AWS_DEV, AWS_QA],
      regions: [
        { id: "us-east-1", name: "us-east-1", cloud_type: "aws_cnr" },
        { id: "us-west-1", name: "us-west-1", cloud_type: "aws_cnr" },
        { id: "eu-west-1", name: "eu-west-1", cloud_type: "aws_cnr" },
        { id: "ap-southeast-2", name: "ap-southeast-2", cloud_type: "aws_cnr" },
        { id: "ap-northeast-2", name: "ap-northeast-2", cloud_type: "aws_cnr" }
      ],
      instance_types: [
        { name: "p4", cloud_type: "aws_cnr" },
        { name: "p3", cloud_type: "aws_cnr" },
        { name: "g4ad", cloud_type: "aws_cnr" },
        { name: "m5", cloud_type: "aws_cnr" },
        { name: "t3a", cloud_type: "aws_cnr" },
        { name: "r7g", cloud_type: "aws_cnr" },
        { name: "i4i", cloud_type: "aws_cnr" }
      ],
      budget: 120,
      last_runset_cost: lastTemplateRunsetCost,
      name_prefix: "my-ml-run",
      tags: {
        ml_value: "ml_tag"
      },
      hyperparameters: {
        "Model URL": "MODEL_URL",
        "Dataset URL": "DATASET_URL",
        "Learning rate": "LEARNING_RATE"
      },
      total_cost: runsetRuns.reduce((acc, { cost }) => acc + cost, 0),
      total_runs: runsetRuns.length
    };
  });

const getRunsetTemplate = (runsetTemplateId) => getRunsetTemplates().find(({ id }) => id === runsetTemplateId);

const getModelRuns = (modelId) => {
  const model = models.find(({ id }) => id === modelId);

  if (!model) {
    return [];
  }

  const modelRuns = model.runs
    .map(getRun)
    .filter((run) => run !== undefined)
    .map((run) => {
      const runsetTemplate = getRunsetTemplate(run.runset_template_id);

      return {
        ...run,
        runset_template: runsetTemplate
          ? {
              name: runsetTemplate.name,
              id: runsetTemplate.id
            }
          : null
      };
    });

  return modelRuns;
};

const _getModelInfo = (model) => {
  const modelRuns = getModelRuns(model.id);

  if (modelRuns.length !== 0) {
    const lastRun = modelRuns[0];
    const lastSuccessfulRun = modelRuns.find(({ status }) => status === ML_RUN_STATUS.COMPLETED) ?? {};

    const modelExecutors = getModelExecutors(model.id);

    const lastRunExecutors = getRunExecutors(lastRun.id);

    const last30DaysCost = modelRuns.reduce((acc, curr) => acc + curr.cost, 0);

    return {
      last_run: lastRun.start,
      last_run_cost: lastRun.cost,
      last_run_duration: lastRun.duration,
      last_run_executor: lastRunExecutors.length !== 0 ? lastRunExecutors[0] ?? null : null,
      last_successful_run: lastSuccessfulRun.start,
      run_goals:
        lastSuccessfulRun.goals?.map((goal) => ({
          ...goal,
          last_run_value: lastSuccessfulRun.data[goal.key],
          history: modelRuns
            .map((run) => run.data?.[goal.key])
            .filter((value) => value !== undefined)
            .reverse()
        })) ?? [],
      last_run_reached_goals: Object.fromEntries(
        model.goals.map((goal) => [
          goal.key,
          {
            ...goal,
            value: lastSuccessfulRun.data?.[goal.key],
            reached: isParameterReached(goal.key, lastSuccessfulRun.data?.[goal.key])
          }
        ])
      ),
      executors: modelExecutors,
      executors_count: modelExecutors.length,
      runs_count: modelRuns.length,
      last_30_days_cost: last30DaysCost,
      total_cost: last30DaysCost * 2.5,
      status: lastRun.status
    };
  }

  return {
    last_run: 0,
    last_run_cost: 0,
    last_run_duration: 0,
    last_run_executor: null,
    last_successful_run: 0,
    run_goals: [],
    executors: [],
    executors_count: 0,
    runs_count: 0,
    total_cost: 0,
    last_30_days_cost: 0,
    status: ML_MODEL_STATUS.CREATED
  };
};

const getModels = () =>
  models.map((model) => ({
    ...model,
    ..._getModelInfo(model)
  }));

const getModel = (modelId) => getModels().find(({ id }) => id === modelId);

const getRunDetails = (runId) => {
  const run = getRun(runId);

  if (run) {
    return {
      ...run,
      application: getModel(run.application_id)
    };
  }

  return {};
};

const getRunBreakdown = (runId) =>
  runBreakdowns[runId] ?? {
    breakdown: {},
    milestones: [],
    stages: []
  };

const getExecutorsBreakdown = (breakdownBy) => executorsBreakdown[breakdownBy] ?? {};

const getExecutors = () => executors;

const getRunset = (runsetId) => {
  const runset = runsets.find(({ id }) => id === runsetId);

  if (!runset) {
    return {};
  }

  const runsetRuns = runset.runs
    .map((runId) => {
      const run = getRun(runId);
      if (!run) {
        return undefined;
      }

      const runExecutor = getExecutor(run.executor_id) ?? {};

      return {
        ...run,
        goals: run.goals.map((goal) => ({
          ...goal,
          value: run.data?.[goal.key]
        })),
        executors: [runExecutor]
      };
    })
    .filter((r) => r !== undefined)
    .sort(({ number: numberA }, { number: numberB }) => numberA - numberB);

  const [firstRun = {}] = [...runsetRuns].reverse();

  return {
    ...runset,
    application: getModel(runset.application_id),
    runs_count: runsetRuns.length,
    started_at: firstRun.start,
    template: getRunsetTemplate(runset.template_id),
    duration: runsetRuns.reduce((acc, { duration }) => acc + duration, 0),
    succeeded_runs: runsetRuns.filter((run) => {
      const goalsMetStatus = getGoalsStatus(
        run.goals.map((goal) => ({
          tendency: goal.tendency,
          targetValue: goal.target_value,
          value: run.data[goal.key]
        }))
      );

      return goalsMetStatus === GOAL_STATUS.MET;
    }).length,
    cost: runsetRuns.reduce((acc, { cost }) => acc + cost, 0),
    runs: runsetRuns
  };
};

const getRunsets = (runsetTemplateId) => {
  const runsetTemplate = getRunsetTemplate(runsetTemplateId);

  if (!runsetTemplate) {
    return {
      runsets: [],
      runsCount: 0,
      totalCost: 0,
      lastRunsetCost: 0
    };
  }

  const templateRunsets = runsetTemplate.runsets.map((runset) => getRunset(runset.id));

  return {
    runsets: templateRunsets,
    runsCount: templateRunsets.reduce((acc, runset) => acc + runset.runs.length, 0),
    totalCost: templateRunsets.reduce((acc, runset) => acc + runset.expenses, 0),
    lastRunsetCost: templateRunsets[0]?.expenses ?? 0
  };
};

const getModelRecommendations = () => ({
  ...modelRecommendations,
  total_count: Object.values(modelRecommendations.optimizations).reduce((acc, { count = 0 }) => acc + count, 0),
  total_saving: Object.values(modelRecommendations.optimizations).reduce((acc, { saving = 0 }) => acc + saving, 0)
});

const getDataSources = () => dataSources;

export {
  getModels,
  getRunDetails,
  getRunBreakdown,
  getRunExecutors,
  getRunsetExecutors,
  getModel,
  getModelExecutors,
  getModelRuns,
  getExecutorsBreakdown,
  getExecutors,
  getRunsetTemplates,
  getRunsetTemplate,
  getRunsets,
  getRunset,
  getModelRecommendations,
  getDataSources
};
