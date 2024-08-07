import { useState } from "react";
import { Stack } from "@mui/material";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlTaskExecutorsContainer from "containers/MlTaskExecutorsContainer";
import MlTaskLeaderboardContainer from "containers/MlTaskLeaderboardContainer";
import MlTaskModelVersionsContainer from "containers/MlTaskModelVersionsContainer";
import MlTaskRecommendationsContainer from "containers/MlTaskRecommendationsContainer";
import MlTaskRunsListContainer from "containers/MlTaskRunsListContainer";
import MlTaskSummaryCardsContainer from "containers/MlTaskSummaryCardsContainer";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { ML_TASK_DETAILS_TABS, ML_TASK_DETAILS_TAB_NAME, OPTSCALE_MODE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import TaskActionBar from "./TaskActionBar";
import TaskDetailsSummary from "./TaskDetailsSummary";

const Tabs = ({ task, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const tabs = [
    {
      title: ML_TASK_DETAILS_TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: <TaskDetailsSummary task={task} isTaskDetailsLoading={isLoading} />
    },
    {
      title: ML_TASK_DETAILS_TABS.RUNS,
      dataTestId: "tab_runs",
      node: <MlTaskRunsListContainer />
    },
    {
      title: ML_TASK_DETAILS_TABS.MODEL_VERSIONS,
      dataTestId: "tab_model_versions",
      node: <MlTaskModelVersionsContainer />
    },
    {
      title: ML_TASK_DETAILS_TABS.LEADERBOARDS,
      dataTestId: "tab_leaderboards",
      node: <MlTaskLeaderboardContainer task={task} />
    },
    ...(isFinOpsEnabled
      ? [
          {
            title: ML_TASK_DETAILS_TABS.RECOMMENDATIONS,
            dataTestId: "tab_recommendations",
            node: <MlTaskRecommendationsContainer />
          }
        ]
      : []),
    {
      title: ML_TASK_DETAILS_TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <MlTaskExecutorsContainer />
    }
  ];

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <MlTaskSummaryCardsContainer task={task} isTaskDetailsLoading={isLoading} />
      </div>
      <div>
        <TabsWrapper
          tabsProps={{
            tabs,
            queryTabName: ML_TASK_DETAILS_TAB_NAME,
            defaultTab: ML_TASK_DETAILS_TABS.OVERVIEW,
            name: "ml-task-run-details",
            activeTab,
            handleChange: (event, value) => {
              setActiveTab(value);
            }
          }}
        />
      </div>
    </Stack>
  );
};

const MlTaskDetails = ({ task = {}, isLoading = false, isDataReady = true }) => (
  <>
    <TaskActionBar name={task.name} isDataReady={isDataReady} taskKey={task.key} taskId={task.id} isLoading={isLoading} />
    <PageContentWrapper>
      <Tabs task={task} isLoading={isLoading} />
    </PageContentWrapper>
  </>
);

export default MlTaskDetails;
