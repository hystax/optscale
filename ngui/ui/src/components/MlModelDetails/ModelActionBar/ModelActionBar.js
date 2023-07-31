import React from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { Link } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_MODEL, GET_ML_MODEL_RECOMMENDATIONS, GET_ML_MODEL_RUNS, GET_ML_EXECUTORS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { getEditMlModelUrl, ML_MODELS } from "urls";

const ModelActionBar = ({ isLoading, name, modelKey, modelId }) => {
  const openSideModal = useOpenSideModal();

  const refetch = useRefetchApis();

  const baseActionBarItems = [
    {
      key: "btn-refresh",
      icon: <RefreshOutlinedIcon fontSize="small" />,
      messageId: "refresh",
      dataTestId: "btn_refresh",
      type: "button",
      action: () => {
        refetch([GET_ML_MODEL, GET_ML_MODEL_RECOMMENDATIONS, GET_ML_MODEL_RUNS, GET_ML_EXECUTORS]);
      }
    },
    {
      key: "btn-profiling-integration",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "profilingIntegration",
      dataTestId: "btn_profiling_integration",
      type: "button",
      action: () => openSideModal(ProfilingIntegrationModal, { modelKey })
    },
    {
      key: "edit",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "configure",
      link: getEditMlModelUrl(modelId),
      type: "button",
      isLoading,
      requiredActions: ["EDIT_PARTNER"],
      dataTestId: "btn_edit"
    }
  ];

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_MODELS} component={RouterLink}>
        <FormattedMessage id="models" />
      </Link>
    ],
    title: {
      text: name,
      isLoading,
      dataTestId: "lbl_model_overview"
    },
    items: baseActionBarItems
  };

  return <ActionBar data={actionBarDefinition} />;
};

ModelActionBar.propTypes = {
  modelKey: PropTypes.string.isRequired,
  isLoading: PropTypes.bool,
  name: PropTypes.string,
  modelId: PropTypes.string
};

export default ModelActionBar;
