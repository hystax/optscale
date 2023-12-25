import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlEditModelFormContainer from "containers/MlEditModelFormContainer";
import MlEditModelLeaderboardContainer from "containers/MlEditModelLeaderboardContainer";
import MlEditModelParametersContainer from "containers/MlEditModelParametersContainer";
import { ML_TASKS, getMlModelDetailsUrl } from "urls";
import { isEmpty as isEmptyObject } from "utils/objects";

const SETTING_TABS = Object.freeze({
  COMMON: "common",
  PARAMETERS: "metrics",
  LEADERBOARDS: "leaderboards"
});

const MlEditModel = ({ leaderboard, model, isLoading = false }) => {
  const { id, name } = model;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={getMlModelDetailsUrl(id)} component={RouterLink}>
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
      node: <MlEditModelFormContainer model={model} />
    },
    {
      title: SETTING_TABS.PARAMETERS,
      dataTestId: "tab_metrics",
      node: <MlEditModelParametersContainer modelParameters={model.goals ?? []} />
    },
    ...(!isEmptyObject(leaderboard)
      ? [
          {
            title: SETTING_TABS.LEADERBOARDS,
            dataTestId: "tab_leaderboard",
            node: <MlEditModelLeaderboardContainer leaderboard={leaderboard} task={model} />
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
            name: "edit-model"
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default MlEditModel;
