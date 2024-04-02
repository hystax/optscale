import { useState } from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_EXECUTORS, GET_ML_RUN_DETAILS, GET_ML_RUN_DETAILS_BREAKDOWN } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import ExecutionBreakdownContainer from "containers/ExecutionBreakdownContainer";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_TASKS, getMlTaskDetailsUrl } from "urls";
import { SPACING_2 } from "utils/layouts";
import { formatRunFullName } from "utils/ml";
import { Executors, Overview } from "./Components";
import Status from "./Components/Status";

const TABS = Object.freeze({
  OVERVIEW: "overview",
  CHARTS: "charts",
  EXECUTORS: "executors"
});

const Tabs = ({ run, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: (
        <Overview
          status={run.status}
          duration={run.duration}
          cost={run.cost}
          reachedGoals={run.reached_goals}
          dataset={run.dataset}
          tags={run.tags}
          hyperparameters={run.hyperparameters}
          git={run.git}
          command={run.command}
          console={run.console}
          isLoading={isLoading}
        />
      )
    },
    {
      title: TABS.CHARTS,
      dataTestId: "tab_charts",
      node: <ExecutionBreakdownContainer reachedGoals={run.reached_goals} />
    },
    {
      title: TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <Executors />
    }
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: TABS.OVERVIEW,
        name: "ml-task-run-details",
        activeTab,
        handleChange: (event, value) => {
          setActiveTab(value);
        }
      }}
    />
  );
};

const MlTaskRun = ({ run, isLoading = false }) => {
  const { task: { id: taskId, name: taskName } = {}, name: runName, number } = run;

  const refetch = useRefetchApis();

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={getMlTaskDetailsUrl(taskId)} component={RouterLink}>
        {taskName}
      </Link>,
      <FormattedMessage key={3} id="runs" />
    ],
    title: {
      isLoading,
      text: <Typography>{formatRunFullName(number, runName)}</Typography>
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_RUN_DETAILS, GET_ML_EXECUTORS, GET_ML_RUN_DETAILS_BREAKDOWN])
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Status status={run.status} duration={run.duration} cost={run.cost} isLoading={isLoading} />
          </div>
          <div>
            <Tabs run={run} isLoading={isLoading} />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlTaskRun;
