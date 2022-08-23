import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ArrowForwardIosOutlinedIcon from "@mui/icons-material/ArrowForwardIosOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import DoubleArrowOutlinedIcon from "@mui/icons-material/DoubleArrowOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import RepeatOutlinedIcon from "@mui/icons-material/RepeatOutlined";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import CircleLabel from "components/CircleLabel";
import KeyValueLabel from "components/KeyValueLabel";
import PoolLabel from "components/PoolLabel";
import { DeleteAssignmentRuleModal, ReapplyRulesetModal } from "components/SideModalManager/SideModals";
import SlicedText from "components/SlicedText";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import {
  getCreateAssignmentRuleUrl,
  getEditAssignmentRuleUrl,
  getCreatePoolAssignmentRuleUrl,
  getEditPoolAssignmentRuleUrl
} from "urls";
import { CONDITION_TYPES, TAG_IS, CLOUD_IS, TAG_VALUE_STARTS_WITH } from "utils/constants";

const isPriorityActionDisabled = (priority, condition) => priority === condition;

const getColumns = (tableActions, poolId) => {
  const columns = [
    {
      Header: (
        <TextWithDataTestId dataTestId="lbl_name">
          <FormattedMessage id="name" />
        </TextWithDataTestId>
      ),
      accessor: "name",
      Cell: ({ row: { original } }) => (
        <CircleLabel
          figureColor={original.active ? "success" : "info"}
          label={<SlicedText limit={32} text={original.name} />}
          tooltip={{ show: true, messageId: original.active ? "active" : "inactive", placement: "right" }}
        />
      )
    },
    {
      Header: (
        <TextWithDataTestId dataTestId="lbl_conditions">
          <FormattedMessage id="conditions" />
        </TextWithDataTestId>
      ),
      accessor: "conditionsObject.conditionsString",
      disableSortBy: false,
      Cell: ({ row: { original } }) => original.conditionsObject.conditionsRender
    },
    {
      Header: (
        <TextWithDataTestId dataTestId="lbl_actions">
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      disableSortBy: false,
      id: "actions",
      Cell: ({ row: { id, original } }) => (
        <TableCellActions
          items={tableActions.map((item) => ({
            key: item.messageId,
            messageId: item.messageId,
            color: item.color,
            dataTestId: `${item.dataTestId}_${id}`,
            disabled: item.disabledPriority ? isPriorityActionDisabled(original.priority, item.disabledPriority) : false,
            icon: item.icon,
            action: () => item.action(original.id)
          }))}
        />
      )
    }
  ];
  if (poolId) {
    columns.splice(1, 0, {
      Header: (
        <TextWithDataTestId dataTestId="lbl_owner">
          <FormattedMessage id="owner" />
        </TextWithDataTestId>
      ),
      accessor: "owner_name"
    });
  } else {
    columns.splice(1, 0, {
      Header: (
        <TextWithDataTestId dataTestId="lbl_assign">
          <FormattedMessage id="assignTo" />
        </TextWithDataTestId>
      ),
      accessor: "pool/owner",
      Cell: ({ row: { original } }) => (
        <CaptionedCell caption={original.owner_name}>
          <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />
        </CaptionedCell>
      )
    });
    columns.splice(columns.length - 1, 0, {
      Header: (
        <TextWithDataTestId dataTestId="lbl_priority">
          <FormattedMessage id="priority" />
        </TextWithDataTestId>
      ),
      accessor: "priority",
      defaultSort: "asc"
    });
  }
  return columns;
};

const AssignmentRulesTable = ({ rules, poolId, isLoading, onUpdatePriority }) => {
  const intl = useIntl();
  const navigate = useNavigate();
  const openSideModal = useOpenSideModal();

  const { rules: assignmentRules = [], entities = {} } = rules || {};

  const rulesCount = assignmentRules.length;

  const tableData = useMemo(() => {
    const translateType = (type) =>
      intl.formatMessage({
        id: CONDITION_TYPES[type]
      });

    const getConditionsObject = (conditions) =>
      [...conditions]
        // sort by translated values in asc order: "name_ends_with" -> "name ends with"
        .sort((a, b) => {
          const aTranslatedTypeInLowerCase = translateType(a.type).toLowerCase();
          const bTranslatedTypeInLowerCase = translateType(b.type).toLowerCase();
          if (aTranslatedTypeInLowerCase > bTranslatedTypeInLowerCase) {
            return 1;
          }
          if (aTranslatedTypeInLowerCase < bTranslatedTypeInLowerCase) {
            return -1;
          }
          return 0;
        })
        .reduce(
          (resultObject, { id, type, meta_info: metaInfo }) => {
            let value = metaInfo;
            if ([TAG_VALUE_STARTS_WITH, TAG_IS].includes(type)) {
              try {
                const metaObj = JSON.parse(metaInfo);
                value = JSON.stringify({ [metaObj.key]: metaObj.value });
              } catch (err) {
                console.log(err);
              }
            }
            if (type === CLOUD_IS) {
              value = entities?.[metaInfo]?.name;
            }
            return {
              ...resultObject,
              conditionsString: `${resultObject.conditionsString ? `${resultObject.conditionsString},` : ""}${translateType(
                type
              )}: ${value}`,
              conditionsRender: [
                ...resultObject.conditionsRender,
                <KeyValueLabel key={id} messageId={CONDITION_TYPES[type]} value={value} />
              ]
            };
          },
          {
            conditionsString: "",
            conditionsRender: []
          }
        );

    return poolId
      ? assignmentRules.map(({ conditions = {}, ...rest }) => ({
          ...rest,
          conditionsObject: getConditionsObject(conditions)
        }))
      : assignmentRules.map(({ conditions = {}, ...rest }) => ({
          ...rest,
          "pool/owner": `${rest.pool_name} ${rest.owner_name}`,
          conditionsObject: getConditionsObject(conditions)
        }));
  }, [assignmentRules, poolId, entities, intl]);

  const addButtonAction = () => navigate(poolId ? getCreatePoolAssignmentRuleUrl(poolId) : getCreateAssignmentRuleUrl());

  const columns = useMemo(() => {
    const editIconAction = (rowDataRuleId) =>
      navigate(poolId ? getEditPoolAssignmentRuleUrl(poolId, rowDataRuleId) : getEditAssignmentRuleUrl(rowDataRuleId));

    const basicActions = [
      {
        messageId: "edit",
        icon: <EditOutlinedIcon />,
        action: (rowDataId) => editIconAction(rowDataId),
        dataTestId: "btn_edit"
      },
      {
        messageId: "delete",
        icon: <DeleteOutlinedIcon />,
        action: (rowDataId) => openSideModal(DeleteAssignmentRuleModal, { ruleId: rowDataId }),
        dataTestId: "btn_delete",
        color: "error"
      }
    ];

    const priorityActions = [
      {
        messageId: "prioritize",
        disabledPriority: 1,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_prioritize",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "prioritize");
        }
      },
      {
        messageId: "promote",
        disabledPriority: 1,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(-90deg)" }} />,
        dataTestId: "btn_promote",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "promote");
        }
      },
      {
        messageId: "demote",
        disabledPriority: rulesCount,
        icon: <ArrowForwardIosOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_demote",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "demote");
        }
      },
      {
        messageId: "deprioritize",
        disabledPriority: rulesCount,
        icon: <DoubleArrowOutlinedIcon style={{ transform: "rotate(90deg)" }} />,
        dataTestId: "btn_deprioritize",
        action: (rowDataId) => {
          onUpdatePriority(rowDataId, "deprioritize");
        }
      }
    ];
    const tableActions = poolId ? basicActions : [...priorityActions, ...basicActions];
    return getColumns(tableActions, poolId);
  }, [rulesCount, poolId, navigate, onUpdatePriority, openSideModal]);

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
        action: addButtonAction
      },
      ...(poolId
        ? []
        : [
            {
              key: "bu-reapply",
              icon: <RepeatOutlinedIcon fontSize="small" />,
              messageId: "reapplyRuleset",
              type: "button",
              action: () => openSideModal(ReapplyRulesetModal),
              dataTestId: "btn_re_apply"
            }
          ])
    ]
  };

  return isLoading ? (
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
          definition: actionBarDefinition
        }}
        dataTestIds={{
          container: "table_rules"
        }}
      />
    </>
  );
};

AssignmentRulesTable.propTypes = {
  rules: PropTypes.object.isRequired,
  poolId: PropTypes.string,
  isLoading: PropTypes.bool,
  onUpdatePriority: PropTypes.func
};

export default AssignmentRulesTable;
