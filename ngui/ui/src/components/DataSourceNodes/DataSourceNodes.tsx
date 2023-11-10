import SettingsIcon from "@mui/icons-material/Settings";
import DataSourceNodesTable from "components/DataSourceNodesTable";
import { UpdateCostModelModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const DataSourceNodes = ({ cloudAccountId, costModel = {}, nodes, isLoading = false }) => {
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

export default DataSourceNodes;
