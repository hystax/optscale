import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ArrowForwardIosOutlinedIcon from "@mui/icons-material/ArrowForwardIosOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import DoubleArrowOutlinedIcon from "@mui/icons-material/DoubleArrowOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import RepeatOutlinedIcon from "@mui/icons-material/RepeatOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import DeleteAssignmentRuleModal from "components/SideModalManager/SideModals/DeleteAssignmentRuleModal";
import ReapplyRulesetModal from "components/SideModalManager/SideModals/ReapplyRulesetModal";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { getCreateAssignmentRuleUrl, getEditAssignmentRuleUrl } from "urls";
import { isEmptyArray } from "utils/arrays";
import { conditions, name, poolOwner, priority } from "./columns";
import prepareData from "./utils/prepareData";

const AssignmentRulesTable = ({ rules, managedPools, isLoadingProps = {}, onUpdatePriority }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { isGetAssignmentRulesLoading, isGetManagedPoolsLoading } = isLoadingProps;

  const isManageAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const navigate = useNavigate();

  const openSideModal = useOpenSideModal();

  const { rules: assignmentRules = [], entities = {} } = rules || {};

  const rulesCount = assignmentRules.length;

  const tableData = useMemo(
    () =>
      prepareData({
        assignmentRules,
        entities,
      }),
    [assignmentRules, entities]
  );

  const addButtonAction = () => navigate(getCreateAssignmentRuleUrl());

  const columns = useMemo(() => {
    const basicActions = [
      {
        messageId: "edit",
        icon: <EditOutlinedIcon />,
        action: (rowDataId) => navigate(getEditAssignmentRuleUrl(rowDataId)),
        dataTestId: "btn_edit",
      },
      {
        messageId: "delete",
        icon: <DeleteOutlinedIcon />,
        action: (rowDataId) => openSideModal(DeleteAssignmentRuleModal, { ruleId: rowDataId }),
        dataTestId: "btn_delete",
        color: "error",
      },
    ];

    const priorityActions = [
      {
        messageId: "prioritize",
        disabledPriority: 1,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_prioritize",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "prioritize");
        },
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      },
      {
        messageId: "promote",
        disabledPriority: 1,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_promote",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "promote");
        },
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      },
      {
        messageId: "demote",
        disabledPriority: rulesCount,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_demote",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "demote");
        },
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      },
      {
        messageId: "deprioritize",
        disabledPriority: rulesCount,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_deprioritize",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "deprioritize");
        },
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      },
    ];

    return [
      name(),
      poolOwner(),
      conditions(),
      priority(),
      ...(isManageAllowed
        ? [
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_actions">
                  <FormattedMessage id="actions" />
                </TextWithDataTestId>
              ),
              enableSorting: false,
              id: "actions",
              cell: ({ row: { id, original } }) => (
                <TableCellActions
                  items={[
                    ...priorityActions.map((item) => ({
                      key: item.messageId,
                      messageId: item.messageId,
                      dataTestId: `${item.dataTestId}_${id}`,
                      disabled: item.disabled || original.priority === item.disabledPriority,
                      icon: item.icon,
                      tooltip: item.tooltip,
                      action: () => item.action(original.id),
                    })),
                    ...basicActions.map((item) => ({
                      key: item.messageId,
                      messageId: item.messageId,
                      icon: item.icon,
                      action: () => item.action(original.id),
                      dataTestId: `${item.dataTestId}_${id}`,
                      color: item.color,
                    })),
                  ]}
                />
              ),
            },
          ]
        : []),
    ];
  }, [isRestricted, restrictionReasonMessage, rulesCount, isManageAllowed, navigate, openSideModal, onUpdatePriority]);

  const actionBarDefinition = {
    items: [
      {
        key: "bu-add",
        icon: <AddOutlinedIcon fontSize="small" />,
        messageId: "add",
        color: "success",
        variant: "contained",
        type: "button",
        dataTestId: "btn_add",
        action: addButtonAction,
        requiredActions: ["EDIT_PARTNER"],
      },
      {
        key: "bu-reapply",
        icon: <RepeatOutlinedIcon fontSize="small" />,
        messageId: "reapplyRuleset",
        type: "button",
        action: () => openSideModal(ReapplyRulesetModal, { managedPools }),
        dataTestId: "btn_re_apply",
        show: !isEmptyArray(managedPools),
        isLoading: isGetManagedPoolsLoading,
      },
    ],
  };

  return isGetAssignmentRulesLoading ? (
    <TableLoader columnsCounter={4} showHeader />
  ) : (
    <>
      <Table
        withSearch
        data={tableData}
        columns={columns}
        localization={{ emptyMessageId: "noAutomaticResourceAssignmentRules" }}
        actionBar={{
          show: true,
          definition: actionBarDefinition,
        }}
        pageSize={50}
        dataTestIds={{
          container: "table_rules",
        }}
      />
    </>
  );
};

export default AssignmentRulesTable;
