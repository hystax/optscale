import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlEditTaskFormContainer from "containers/MlEditTaskFormContainer";
import MlEditTaskLeaderboardTemplateContainer from "containers/MlEditTaskLeaderboardTemplateContainer";
import MlEditTaskMetricsContainer from "containers/MlEditTaskMetricsContainer";
import { ML_TASKS, getMlTaskDetailsUrl } from "urls";
import { isEmpty as isEmptyObject } from "utils/objects";

const SETTING_TABS = Object.freeze({
  COMMON: "common",
  METRICS: "metrics",
  LEADERBOARD_TEMPLATE: "leaderboardTemplate"
});

const MlEditTask = ({ leaderboardTemplate, task, isLoading = false }) => {
  const { id, name } = task;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={getMlTaskDetailsUrl(id)} component={RouterLink}>
        {name}
      </Link>
    ],
    title: {
      messageId: "editTaskTitle",
      isLoading,
      dataTestId: "lbl_edit_task"
    }
  };

  const tabs = [
    {
      title: SETTING_TABS.COMMON,
      dataTestId: "tab_common",
      node: <MlEditTaskFormContainer task={task} />
    },
    {
      title: SETTING_TABS.METRICS,
      dataTestId: "tab_metrics",
      node: <MlEditTaskMetricsContainer taskMetrics={task.metrics ?? []} />
    },
    ...(!isEmptyObject(leaderboardTemplate)
      ? [
          {
            title: SETTING_TABS.LEADERBOARD_TEMPLATE,
            dataTestId: "tab_leaderboard_template",
            node: <MlEditTaskLeaderboardTemplateContainer leaderboardTemplate={leaderboardTemplate} task={task} />
          }
        ]
      : [])
  ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <TabsWrapper
          isLoading={isLoading}
          tabsProps={{
            tabs,
            defaultTab: SETTING_TABS.COMMON,
            name: "edit-task"
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default MlEditTask;
