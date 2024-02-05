import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import SaveIcon from "@mui/icons-material/Save";
import { Box } from "@mui/material";
import IconButton from "components/IconButton";
import { DeleteMlChartsDashboard, SaveMlChartsDashboard } from "components/SideModalManager/SideModals";
import { isDefaultDashboard } from "hooks/useModelRunChartState";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import NameSelector from "./NameSelector";

const DashboardControls = ({
  currentEmployeeId,
  dashboard,
  dashboards,
  onDashboardChange,
  saved,
  updateDashboard,
  createDashboard,
  removeDashboard,
  isLoadingProps = {}
}) => {
  const isOwnedDashboard = currentEmployeeId === dashboard.ownerId;

  const openSideModal = useOpenSideModal();

  const onSave = () => {
    openSideModal(SaveMlChartsDashboard, {
      dashboard,
      updateDashboard,
      isOwnedDashboard,
      createDashboard
    });
  };

  const onDelete = () => {
    openSideModal(DeleteMlChartsDashboard, { dashboard, removeDashboard });
  };

  return (
    <>
      <Box mr={1}>
        <NameSelector
          currentEmployeeId={currentEmployeeId}
          dashboards={dashboards}
          selected={dashboard.id}
          saved={saved}
          onChange={(id) => {
            onDashboardChange(id);
          }}
          isLoading={isLoadingProps.isSetupLoading || isLoadingProps.isSelectNewLoading}
        />
      </Box>
      <div>
        <IconButton
          icon={<SaveIcon />}
          onClick={onSave}
          isLoading={isLoadingProps.isSetupLoading || isLoadingProps.isSelectNewLoading}
        />
      </div>
      <div>
        <IconButton
          icon={<DeleteOutlinedIcon />}
          color="error"
          onClick={onDelete}
          disabled={!isOwnedDashboard || isDefaultDashboard(dashboard.id)}
          isLoading={isLoadingProps.isSetupLoading || isLoadingProps.isSelectNewLoading}
        />
      </div>
    </>
  );
};

export default DashboardControls;
