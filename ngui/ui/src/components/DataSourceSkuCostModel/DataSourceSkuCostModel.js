import React from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import PropTypes from "prop-types";
import DataSourceNodesTable from "components/DataSourceNodesTable";
import { UpdateCostModelModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const DataSourceSkuCostModel = ({ cloudAccountId, costModel = {}, nodes, isLoading = false }) => {
  const openSideModal = useOpenSideModal();
  const { isDemo } = useOrganizationInfo();

  const actionBarDefinition = {
    items: [
      {
        key: "updateCostModel",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "updateCostModel",
        variant: "text",
        disabled: isDemo,
        action: () => openSideModal(UpdateCostModelModal, { cloudAccountId, costModel }),
        type: "button",
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
        dataTestId: "btn_update_cost_model"
      }
    ]
  };

  return (
    <DataSourceNodesTable
      nodes={nodes}
      isLoading={isLoading}
      actionBar={{
        show: !isDemo,
        definition: actionBarDefinition
      }}
    />
  );
};

DataSourceSkuCostModel.propTypes = {
  nodes: PropTypes.array.isRequired,
  cloudAccountId: PropTypes.string.isRequired,
  costModel: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default DataSourceSkuCostModel;
