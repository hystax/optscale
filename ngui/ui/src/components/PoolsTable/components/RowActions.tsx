import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import { useNavigate } from "react-router-dom";
import { AddPoolModal, DeletePoolModal } from "components/SideModalManager/SideModals";
import TableCellActions from "components/TableCellActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { getThisMonthPoolExpensesUrl, getThisMonthResourcesByPoolUrl } from "urls";
import { SCOPE_TYPES } from "utils/constants";

const RowActions = ({ row }) => {
  const { parent_id: parentId, id, hasChildren, name, unallocated_limit: unallocatedLimit } = row.original;

  const navigate = useNavigate();

  const openSideModal = useOpenSideModal();

  const getDeleteTooltip = () => {
    if (!parentId) {
      return "organizationPoolCannotBeDeleted";
    }
    if (hasChildren) {
      return "poolWithSubpoolsCannotBeDeleted";
    }
    return "delete";
  };

  const tableActions = [
    {
      key: "add",
      icon: <AddCircleOutlineIcon />,
      messageId: "addSubPool",
      action: (e) => {
        e.stopPropagation();
        openSideModal(AddPoolModal, { parentId: id, parentPoolName: name, unallocatedLimit });
      },
      requiredActions: ["MANAGE_POOLS"],
      dataTestId: "btn_add"
    },
    {
      key: "seeResourceList",
      messageId: "seeResourceList",
      icon: <StorageOutlinedIcon />,
      action: (e) => {
        e.stopPropagation();
        navigate(getThisMonthResourcesByPoolUrl(id));
      },
      dataTestId: "btn_see_rl"
    },
    {
      key: "seeInCostExplorer",
      messageId: "seeInCostExplorer",
      icon: <BarChartOutlinedIcon />,
      action: (e) => {
        e.stopPropagation();
        navigate(getThisMonthPoolExpensesUrl(id));
      },
      dataTestId: `btn_see_in_ce_${row.id}`
    },
    {
      key: "delete",
      messageId: getDeleteTooltip(),
      icon: <DeleteOutlinedIcon />,
      color: "error",
      disabled: hasChildren || !parentId,
      action: (e) => {
        e.stopPropagation();
        openSideModal(DeletePoolModal, { poolId: id });
      },
      dataTestId: `btn_delete_${row.id}`,
      requiredActions: ["MANAGE_POOLS"]
    }
  ];

  return <TableCellActions entityType={SCOPE_TYPES.POOL} entityId={row.original.id} items={tableActions} />;
};

export default RowActions;
