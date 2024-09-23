import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ArrowForwardIosOutlinedIcon from "@mui/icons-material/ArrowForwardIosOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import DoubleArrowOutlinedIcon from "@mui/icons-material/DoubleArrowOutlined";
import RepeatOutlinedIcon from "@mui/icons-material/RepeatOutlined";
import { FormattedMessage } from "react-intl";
import { DeleteClusterTypeModal, ReapplyClusterTypesModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { CLUSTER_TYPE_CREATE } from "urls";

const ClusterTypesTable = ({ clusterTypes, onUpdatePriority, isLoading = false }) => {
  const openSideModal = useOpenSideModal();
  const isManageResourcesAllowed = useIsAllowed({ requiredActions: ["MANAGE_RESOURCES"] });

  const memoizedClusterTypes = useMemo(() => clusterTypes, [clusterTypes]);

  const columns = useMemo(() => {
    const basicActions = [
      {
        key: "delete",
        messageId: "delete",
        icon: <DeleteOutlinedIcon />,
        action: ({ id, name }) => openSideModal(DeleteClusterTypeModal, { clusterTypeId: id, clusterTypeName: name }),
        dataTestId: "btn_delete",
        color: "error"
      }
    ];

    const clusterTypesCount = memoizedClusterTypes.length;

    const priorityActions = [
      {
        messageId: "prioritize",
        disabledPriority: 1,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_prioritize",
        action: ({ id }) => {
          onUpdatePriority(id, "prioritize");
        }
      },
      {
        messageId: "promote",
        disabledPriority: 1,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_promote",
        action: ({ id }) => {
          onUpdatePriority(id, "promote");
        }
      },
      {
        messageId: "demote",
        disabledPriority: clusterTypesCount,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_demote",
        action: ({ id }) => {
          onUpdatePriority(id, "demote");
        }
      },
      {
        messageId: "deprioritize",
        disabledPriority: clusterTypesCount,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_deprioritize",
        action: ({ id }) => {
          onUpdatePriority(id, "deprioritize");
        }
      }
    ];

    const getActionsColumnDefinition = () => ({
      header: (
        <TextWithDataTestId dataTestId="lbl_actions">
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      id: "actions",
      enableSorting: false,
      cell: ({ row: { original, index } }) => (
        <TableCellActions
          items={[
            ...priorityActions.map((item) => ({
              key: item.messageId,
              messageId: item.messageId,
              color: item.color,
              dataTestId: `${item.dataTestId}_${index}`,
              disabled: original.priority === item.disabledPriority,
              icon: item.icon,
              action: () => item.action(original)
            })),
            ...basicActions.map((item) => ({
              ...item,
              dataTestId: `${item.dataTestId}_${index}`,
              action: () => item.action(original)
            }))
          ]}
        />
      )
    });

    const basicColumns = [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tag_key">
            <FormattedMessage id="tagKey" />
          </TextWithDataTestId>
        ),
        accessorKey: "tag_key"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_priority">
            <FormattedMessage id="priority" />
          </TextWithDataTestId>
        ),
        accessorKey: "priority",
        defaultSort: "asc"
      }
    ];

    return isManageResourcesAllowed ? basicColumns.concat(getActionsColumnDefinition()) : basicColumns;
  }, [isManageResourcesAllowed, memoizedClusterTypes.length, onUpdatePriority, openSideModal]);

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table
      actionBar={{
        show: isManageResourcesAllowed,
        definition: {
          items: [
            {
              key: "add",
              icon: <AddOutlinedIcon fontSize="small" />,
              messageId: "add",
              color: "success",
              variant: "contained",
              type: "button",
              link: CLUSTER_TYPE_CREATE,
              dataTestId: "btn_add"
            },
            {
              key: "bu-reapply",
              icon: <RepeatOutlinedIcon fontSize="small" />,
              messageId: "reapplyClusterTypes",
              type: "button",
              action: () => openSideModal(ReapplyClusterTypesModal),
              dataTestId: "btn_re_apply"
            }
          ]
        }
      }}
      data={memoizedClusterTypes}
      columns={columns}
      withSearch
      pageSize={50}
      dataTestIds={{
        searchInput: "input_search",
        searchButton: "btn_search",
        deleteSearchButton: "btn_delete_search"
      }}
      localization={{ emptyMessageId: "noClusterTypes" }}
    />
  );
};

export default ClusterTypesTable;
