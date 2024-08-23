import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  GET_ML_TASK,
  GET_ML_TASK_RECOMMENDATIONS,
  GET_ML_TASK_RUNS,
  GET_ML_EXECUTORS,
  GET_ML_LEADERBOARD_TEMPLATE,
  GET_ML_LEADERBOARDS,
  GET_ML_LEADERBOARD,
  GET_ML_LEADERBOARD_CANDIDATES,
  GET_ML_TASK_TAGS
} from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { getEditMlTaskUrl, ML_TASKS } from "urls";
import { ML_TASK_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";

const TaskActionBar = ({ isLoading, isDataReady, name, taskKey, taskId }) => {
  const openSideModal = useOpenSideModal();

  const navigate = useNavigate();

  const refetch = useRefetchApis();

  const baseActionBarItems = [
    {
      key: "btn-refresh",
      icon: <RefreshOutlinedIcon fontSize="small" />,
      messageId: "refresh",
      dataTestId: "btn_refresh",
      type: "button",
      action: () => {
        refetch([
          GET_ML_TASK,
          GET_ML_TASK_RECOMMENDATIONS,
          GET_ML_TASK_RUNS,
          GET_ML_TASK_TAGS,
          GET_ML_EXECUTORS,
          GET_ML_LEADERBOARD_TEMPLATE,
          GET_ML_LEADERBOARDS,
          GET_ML_LEADERBOARD,
          GET_ML_LEADERBOARD_CANDIDATES
        ]);
      }
    },
    {
      key: "btn-profiling-integration",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "profilingIntegration",
      dataTestId: "btn_profiling_integration",
      type: "button",
      isLoading: !isDataReady,
      action: () => openSideModal(ProfilingIntegrationModal, { taskKey })
    },
    {
      key: "edit",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "configure",
      action: () => {
        const { [ML_TASK_DETAILS_TAB_NAME]: tab } = getQueryParams();
        navigate(
          getEditMlTaskUrl(taskId, {
            [ML_TASK_DETAILS_TAB_NAME]: tab
          })
        );
      },
      type: "button",
      isLoading: !isDataReady,
      requiredActions: ["EDIT_PARTNER"],
      dataTestId: "btn_edit"
    }
  ];

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>
    ],
    title: {
      text: name || "",
      isLoading,
      dataTestId: "lbl_task_overview"
    },
    items: baseActionBarItems
  };

  return <ActionBar data={actionBarDefinition} />;
};

export default TaskActionBar;
