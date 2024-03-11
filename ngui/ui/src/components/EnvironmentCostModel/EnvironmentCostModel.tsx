import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import CostModelFormattedMoney from "components/CostModelFormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { EnvironmentCostModelModal } from "components/SideModalManager/SideModals";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { SCOPE_TYPES } from "utils/constants";

const EnvironmentCostModel = ({ resourceId, hourlyPrice, isLoadingProps = {} }) => {
  const isManageResourcesAllowed = useIsAllowed({
    entityType: SCOPE_TYPES.RESOURCE,
    entityId: resourceId,
    requiredActions: ["MANAGE_RESOURCES"]
  });

  const openSideModal = useOpenSideModal();

  const Body = () => (
    <Box display="flex" alignItems="center">
      <Typography>
        <KeyValueLabel keyMessageId="hourlyPrice" value={<CostModelFormattedMoney value={hourlyPrice} />} />
      </Typography>
      {isManageResourcesAllowed && (
        <IconButton
          key="edit"
          icon={<EditOutlinedIcon />}
          onClick={() => openSideModal(EnvironmentCostModelModal, { resourceId, hourlyPrice })}
          tooltip={{
            show: true,
            messageId: "edit"
          }}
        />
      )}
    </Box>
  );

  const { isGetResourceCostModelLoading = false, isGetPermissionsLoading = false } = isLoadingProps;

  return isGetResourceCostModelLoading || isGetPermissionsLoading ? (
    <Skeleton>
      <Body />
    </Skeleton>
  ) : (
    <Body />
  );
};

export default EnvironmentCostModel;
