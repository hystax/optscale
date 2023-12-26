import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  GET_ML_MODEL,
  GET_ML_MODEL_RECOMMENDATIONS,
  GET_ML_MODEL_RUNS,
  GET_ML_EXECUTORS,
  GET_ML_LEADERBOARD,
  GET_ML_LEADERBOARD_DATASETS,
  GET_ML_LEADERBOARD_DATASET,
  GET_ML_LEADERBOARD_DATASET_DETAILS
} from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { getEditMlModelUrl, ML_TASKS } from "urls";
import { ML_MODEL_DETAILS_TAB_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";

const ModelActionBar = ({ isLoading, isDataReady, name, taskKey, taskId }) => {
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
          GET_ML_MODEL,
          GET_ML_MODEL_RECOMMENDATIONS,
          GET_ML_MODEL_RUNS,
          GET_ML_EXECUTORS,
          GET_ML_LEADERBOARD,
          GET_ML_LEADERBOARD_DATASETS,
          GET_ML_LEADERBOARD_DATASET,
          GET_ML_LEADERBOARD_DATASET_DETAILS
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
        const { [ML_MODEL_DETAILS_TAB_NAME]: tab } = getQueryParams();
        navigate(
          getEditMlModelUrl(taskId, {
            [ML_MODEL_DETAILS_TAB_NAME]: tab
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
      dataTestId: "lbl_model_overview"
    },
    items: baseActionBarItems
  };

  return <ActionBar data={actionBarDefinition} />;
};

export default ModelActionBar;
