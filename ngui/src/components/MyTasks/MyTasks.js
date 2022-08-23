import React, { useMemo } from "react";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import InputOutlinedIcon from "@mui/icons-material/InputOutlined";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Accordion from "components/Accordion";
import Button from "components/Button";
import CaptionedCell from "components/CaptionedCell";
import CloudResourceId from "components/CloudResourceId";
import ConditionWrapper from "components/ConditionWrapper";
import { ConstraintLimitMessage } from "components/ConstraintMessage";
import ConstraintValue from "components/ConstraintValue";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import TaggingPolicyDescriptionShort from "components/OrganizationConstraint/TaggingPolicyDescriptionShort";
import PanelLoader from "components/PanelLoader";
import PoolLabel from "components/PoolLabel";
import ResourceCell from "components/ResourceCell";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TasksOverviewListItem from "components/TasksOverviewListItem";
import WrapperCard from "components/WrapperCard";
import AcceptAssignmentRequestContainer from "containers/AcceptAssignmentRequestContainer";
import HandleAssignmentRequestActionContainer from "containers/HandleAssignmentRequestActionContainer";
import { intl } from "translations/react-intl-config";
import { getResourceUrl, getThisMonthPoolExpensesUrl, getAnomalyUrl, getQuotaAndBudgetUrl, getTaggingPolicyUrl } from "urls";
import {
  DECLINE,
  CANCEL,
  TASK_EXCEEDED_POOL_FORECASTS,
  TASK_INCOMING_ASSIGNMENT_REQUESTS,
  TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  TASK_EXCEEDED_POOLS,
  TASK_VIOLATED_RESOURCE_CONSTRAINTS,
  TASK_VIOLATED_ORGANIZATION_CONSTRAINTS,
  TASK_DIVERGENT_CONSTRAINTS,
  FORMATTED_MONEY_TYPES,
  ANOMALY_TYPES,
  QUOTAS_AND_BUDGETS_TYPES,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  EXPIRING_BUDGET_POLICY,
  TAGGING_POLICY_TYPES
} from "utils/constants";
import { CONSTRAINTS_TYPES } from "utils/constraints";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const getIncomingAssignmentRequestsColumns = () => [
  {
    Header: intl.formatMessage({ id: "id" }),
    accessor: "cloud_resource_id",
    defaultSort: "asc",
    style: RESOURCE_ID_COLUMN_CELL_STYLE,
    Cell: ({ row: { original } }) => (
      <CloudResourceId resourceId={original.resource_id} cloudResourceId={original.cloud_resource_id} />
    )
  },
  {
    Header: intl.formatMessage({ id: "resourceName" }),
    accessor: "resource_name",
    defaultSort: "asc"
  },
  {
    Header: intl.formatMessage({ id: "resourceType" }),
    accessor: "resource_type"
  },
  {
    Header: intl.formatMessage({ id: "pool" }),
    accessor: "source_pool_name",
    Cell: ({ row: { original } }) => (
      <PoolLabel id={original.source_pool_id} name={original.source_pool_name} type={original.source_pool_purpose} />
    )
  },
  {
    Header: intl.formatMessage({ id: "requesterName" }),
    accessor: "requester_name"
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      // TODO: Accept will be integrated into the side model, but in the future need to add a pool selector to the table row
      <Box display="flex">
        <AcceptAssignmentRequestContainer
          resourceName={original.resource_name}
          assignmentRequestId={original.assignment_request_id}
        />
        <HandleAssignmentRequestActionContainer requestId={original.assignment_request_id} action={DECLINE}>
          <IconButton
            color="error"
            icon={<CancelOutlinedIcon />}
            tooltip={{
              show: true,
              value: <FormattedMessage id={DECLINE} />
            }}
          />
        </HandleAssignmentRequestActionContainer>
      </Box>
    )
  }
];

const getOutgoingAssignmentRequestsColumns = () => [
  {
    Header: intl.formatMessage({ id: "id" }),
    accessor: "cloud_resource_id",
    defaultSort: "asc",
    style: RESOURCE_ID_COLUMN_CELL_STYLE,
    Cell: ({ row: { original } }) => (
      <CloudResourceId resourceId={original.resource_id} cloudResourceId={original.cloud_resource_id} />
    )
  },
  {
    Header: intl.formatMessage({ id: "resourceName" }),
    accessor: "resource_name",
    defaultSort: "asc"
  },
  {
    Header: intl.formatMessage({ id: "resourceType" }),
    accessor: "resource_type"
  },
  {
    Header: intl.formatMessage({ id: "pool" }),
    accessor: "source_pool_name",
    Cell: ({ row: { original } }) => (
      <PoolLabel id={original.source_pool_id} name={original.source_pool_name} type={original.source_pool_purpose} />
    )
  },
  {
    Header: intl.formatMessage({ id: "approverName" }),
    accessor: "approver_name"
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      <HandleAssignmentRequestActionContainer requestId={original.assignment_request_id} action={CANCEL}>
        <IconButton
          color={"error"}
          icon={<CancelOutlinedIcon />}
          tooltip={{
            show: true,
            value: <FormattedMessage id={CANCEL} />
          }}
        />
      </HandleAssignmentRequestActionContainer>
    )
  }
];

const getExceededPoolsColumns = () => [
  {
    Header: intl.formatMessage({ id: "pool" }),
    accessor: "pool_name",
    Cell: ({ row: { original } }) => {
      const { pool_name: name, pool_purpose: poolPurpose, pool_id: poolId } = original;
      return <PoolLabel id={poolId} name={name} type={poolPurpose} />;
    }
  },
  {
    Header: intl.formatMessage({ id: "limit" }),
    accessor: "limit",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.limit} />
  },
  {
    Header: intl.formatMessage({ id: "totalExpenses" }),
    accessor: "total_expenses",
    defaultSort: "desc",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.total_expenses} />
  },
  {
    Header: intl.formatMessage({ id: "forecast" }),
    accessor: "forecast",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.forecast} />
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      <IconButton
        icon={<BarChartOutlinedIcon />}
        link={getThisMonthPoolExpensesUrl(original.pool_id)}
        tooltip={{
          show: true,
          value: <FormattedMessage id="seeInCostExplorer" />
        }}
      />
    )
  }
];

const getExceededPoolForecastsColumns = () => [
  {
    Header: intl.formatMessage({ id: "pool" }),
    accessor: "pool_name",
    Cell: ({ row: { original } }) => {
      const { pool_name: name, pool_purpose: poolPurpose, pool_id: poolId } = original;
      return <PoolLabel id={poolId} name={name} type={poolPurpose} />;
    }
  },
  {
    Header: intl.formatMessage({ id: "limit" }),
    accessor: "limit",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.limit} />
  },
  {
    Header: intl.formatMessage({ id: "totalExpenses" }),
    accessor: "total_expenses",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.total_expenses} />,
    defaultSort: "desc"
  },
  {
    Header: intl.formatMessage({ id: "forecast" }),
    accessor: "forecast",
    Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.forecast} />
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      <IconButton
        icon={<BarChartOutlinedIcon />}
        link={getThisMonthPoolExpensesUrl(original.pool_id)}
        tooltip={{
          show: true,
          value: <FormattedMessage id="seeInCostExplorer" />
        }}
      />
    )
  }
];

const extendConstraintsData = (data) =>
  data.map((item) => ({
    ...item,
    resource: `${item.cloud_resource_id} ${item.resource_name}`,
    "pool/owner": `${item.pool_name ?? ""} ${item.owner_name ?? ""}`
  }));

const getViolatedResourceConstraintsColumns = () => [
  {
    Header: intl.formatMessage({ id: "resource" }),
    accessor: "resource",
    defaultSort: "asc",
    style: RESOURCE_ID_COLUMN_CELL_STYLE,
    Cell: ({ row: { original } }) => <ResourceCell rowData={original} />
  },
  {
    Header: intl.formatMessage({ id: "pool/owner" }),
    accessor: "pool/owner",
    style: {
      whiteSpace: "nowrap"
    },
    Cell: ({ row: { original } }) =>
      original.pool_id || original.owner_id ? (
        <CaptionedCell caption={original.owner_id ? original.owner_name : ""}>
          {original.pool_id && <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />}
        </CaptionedCell>
      ) : null
  },
  {
    Header: intl.formatMessage({ id: "type" }),
    accessor: "type",
    Cell: ({ row: { original } }) => <FormattedMessage id={CONSTRAINTS_TYPES[original.type]} />
  },
  {
    Header: intl.formatMessage({ id: "limit" }),
    accessor: "constraint_limit",
    Cell: ({ row: { original } }) => <ConstraintLimitMessage limit={original.constraint_limit} type={original.type} />
  },
  {
    Header: intl.formatMessage({ id: "violatedAt" }),
    accessor: "time",
    Cell: ({ row: { original } }) => format(secondsToMilliseconds(original.time), EN_FULL_FORMAT)
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      <IconButton
        icon={<InputOutlinedIcon />}
        link={`${getResourceUrl(original.resource_id)}?tab=constraints`}
        tooltip={{
          show: true,
          value: <FormattedMessage id="seeResourceConstraints" />
        }}
      />
    )
  }
];

const getViolatedOrganizationConstraintsColumns = () => [
  {
    Header: intl.formatMessage({ id: "policyName" }),
    accessor: "name",
    Cell: ({ cell: { value }, row: { original } }) => {
      let link = "";
      if (ANOMALY_TYPES[original.type]) {
        link = getAnomalyUrl(original.constraint_id);
      }
      if (QUOTAS_AND_BUDGETS_TYPES[original.type]) {
        link = getQuotaAndBudgetUrl(original.constraint_id);
      }
      if (TAGGING_POLICY_TYPES[original.type]) {
        link = getTaggingPolicyUrl(original.constraint_id);
      }
      return (
        <Link color="primary" to={link} component={RouterLink}>
          {value}
        </Link>
      );
    }
  },
  {
    Header: intl.formatMessage({ id: "type" }),
    accessor: "type",
    Cell: ({ row: { original } }) => (
      <FormattedMessage
        id={ANOMALY_TYPES[original.type] || QUOTAS_AND_BUDGETS_TYPES[original.type] || TAGGING_POLICY_TYPES[original.type]}
      />
    )
  },
  {
    Header: intl.formatMessage({ id: "limit" }),
    accessor: "definition",
    Cell: ({
      cell: {
        value: { threshold, max_value: maxValue, monthly_budget: monthlyBudget, total_budget: totalBudget, conditions }
      },
      row: {
        original: { type }
      }
    }) => {
      if (ANOMALY_TYPES[type]) {
        return <KeyValueLabel messageId="threshold" value={`${threshold}%`} />;
      }

      if (TAGGING_POLICY_TYPES[type]) {
        return <TaggingPolicyDescriptionShort conditions={conditions} />;
      }

      return {
        [QUOTA_POLICY]: <KeyValueLabel messageId="quotaPolicyMaxValue" value={maxValue} />,
        [RECURRING_BUDGET_POLICY]: <KeyValueLabel messageId="recurringBudgetPolicyMonthlyBudget" value={monthlyBudget} />,
        [EXPIRING_BUDGET_POLICY]: <KeyValueLabel messageId="budget" value={totalBudget} />
      }[type];
    }
  },
  {
    Header: intl.formatMessage({ id: "value" }),
    accessor: "value",
    Cell: ({ row: { original: { constraint_limit: constraintLimit, type } = {} }, cell: { value } }) => (
      <ConstraintValue hitValue={value} constraintLimit={constraintLimit} type={type} />
    )
  },
  {
    Header: intl.formatMessage({ id: "violatedAt" }),
    accessor: "created_at",
    defaultSort: "desc",
    Cell: ({ row: { original } }) => format(secondsToMilliseconds(original.created_at), EN_FULL_FORMAT)
  }
];

const getDivergentConstraintsColumns = () => [
  {
    Header: intl.formatMessage({ id: "resource" }),
    accessor: "resource",
    defaultSort: "asc",
    style: RESOURCE_ID_COLUMN_CELL_STYLE,
    Cell: ({ row: { original } }) => <ResourceCell rowData={original} />
  },
  {
    Header: intl.formatMessage({ id: "pool/owner" }),
    accessor: "pool/owner",
    style: {
      whiteSpace: "nowrap"
    },
    Cell: ({ row: { original } }) =>
      original.pool_id || original.owner_id ? (
        <CaptionedCell caption={original.owner_id ? original.owner_name : ""}>
          {original.pool_id && <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />}
        </CaptionedCell>
      ) : null
  },
  {
    Header: intl.formatMessage({ id: "type" }),
    accessor: "type",
    Cell: ({ row: { original } }) => <FormattedMessage id={CONSTRAINTS_TYPES[original.type]} />
  },
  {
    Header: intl.formatMessage({ id: "resourceConstraintLimit" }),
    accessor: "limit",
    Cell: ({ row: { original } }) => <ConstraintLimitMessage limit={original.limit} type={original.type} />
  },
  {
    Header: intl.formatMessage({ id: "poolPolicyLimit" }),
    accessor: "policy.limit",
    Cell: ({ row: { original } }) => <ConstraintLimitMessage limit={original.policy.limit} type={original.type} />
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    isStatic: true,
    Cell: ({ row: { original } }) => (
      <IconButton
        icon={<InputOutlinedIcon />}
        link={`${getResourceUrl(original.resource_id)}?tab=constraints`}
        tooltip={{
          show: true,
          value: <FormattedMessage id="seeResourceConstraints" />
        }}
      />
    )
  }
];

const MyTasks = ({ isLoading, isEmpty, data, handleChange, expanded, hasTaskTypeInUrl }) => {
  const tableData = useMemo(() => data, [data]);

  const incomingAssignmentRequestsColumns = useMemo(() => getIncomingAssignmentRequestsColumns(), []);
  const outgoingAssignmentRequestsColumns = useMemo(() => getOutgoingAssignmentRequestsColumns(), []);
  const exceededPoolsColumns = useMemo(() => getExceededPoolsColumns(), []);
  const exceededPoolForecastsColumns = useMemo(() => getExceededPoolForecastsColumns(), []);
  const violatedResourceConstraintsColumns = useMemo(() => getViolatedResourceConstraintsColumns(), []);
  const violatedOrganizationConstraintsColumns = useMemo(() => getViolatedOrganizationConstraintsColumns(), []);
  const divergentConstraintsColumns = useMemo(() => getDivergentConstraintsColumns(), []);

  const tasks = [
    {
      type: TASK_EXCEEDED_POOLS,
      text: "",
      count: tableData?.[TASK_EXCEEDED_POOLS]?.count ?? 0,
      dataTestId: "sp_exceeded_pools",
      table: {
        data: tableData?.[TASK_EXCEEDED_POOLS]?.tasks ?? [],
        columns: exceededPoolsColumns,
        dataTestIds: {
          container: "table_exd_pools"
        },
        localization: {
          emptyMessageId: "noExceededPoolLimits"
        }
      }
    },
    {
      type: TASK_VIOLATED_RESOURCE_CONSTRAINTS,
      text: "",
      count: tableData?.[TASK_VIOLATED_RESOURCE_CONSTRAINTS]?.count ?? 0,
      dataTestId: "sp_violated_resource_constr",
      table: {
        data: extendConstraintsData(tableData?.[TASK_VIOLATED_RESOURCE_CONSTRAINTS]?.tasks ?? []),
        columns: violatedResourceConstraintsColumns,
        dataTestIds: {
          container: "table_violated_resource_constr"
        },
        localization: {
          emptyMessageId: "noViolatedResourceConstraints"
        }
      }
    },
    {
      type: TASK_VIOLATED_ORGANIZATION_CONSTRAINTS,
      text: "",
      count: tableData?.[TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]?.count ?? 0,
      dataTestId: "sp_violated_organization_constr",
      table: {
        data: extendConstraintsData(tableData?.[TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]?.tasks ?? []),
        columns: violatedOrganizationConstraintsColumns,
        dataTestIds: {
          container: "table_violated_organization_constr"
        },
        localization: {
          emptyMessageId: "noViolatedOrganizationConstraints"
        }
      }
    },
    {
      type: TASK_EXCEEDED_POOL_FORECASTS,
      text: "",
      count: tableData?.[TASK_EXCEEDED_POOL_FORECASTS]?.count ?? 0,
      dataTestId: "sp_exceeded_forecasts",
      table: {
        data: tableData?.[TASK_EXCEEDED_POOL_FORECASTS]?.tasks ?? [],
        columns: exceededPoolForecastsColumns,
        dataTestIds: {
          container: "table_exceeded_forecasts"
        },
        localization: {
          emptyMessageId: "noExceededPoolLimitForecasts"
        }
      }
    },
    {
      type: TASK_DIVERGENT_CONSTRAINTS,
      text: "",
      count: tableData?.[TASK_DIVERGENT_CONSTRAINTS]?.count ?? 0,
      dataTestId: "sp_divergent_constraints",
      table: {
        data: extendConstraintsData(tableData?.[TASK_DIVERGENT_CONSTRAINTS]?.tasks ?? []),
        columns: divergentConstraintsColumns,
        dataTestIds: {
          container: "table_divergent_constraints"
        },
        localization: {
          emptyMessageId: "noDivergentConstraints"
        }
      }
    },
    {
      type: TASK_INCOMING_ASSIGNMENT_REQUESTS,
      text: "",
      count: tableData?.[TASK_INCOMING_ASSIGNMENT_REQUESTS]?.count ?? 0,
      dataTestId: "sp_incoming_requests",
      table: {
        data: tableData?.[TASK_INCOMING_ASSIGNMENT_REQUESTS]?.tasks ?? [],
        columns: incomingAssignmentRequestsColumns,
        dataTestIds: {
          container: "table_incoming_requests"
        },
        localization: {
          emptyMessageId: "noIncomingAssignmentRequests"
        }
      }
    },
    {
      type: TASK_OUTGOING_ASSIGNMENT_REQUESTS,
      text: "",
      count: tableData?.[TASK_OUTGOING_ASSIGNMENT_REQUESTS]?.count ?? 0,
      dataTestId: "sp_outgoing_requests",
      table: {
        data: tableData?.[TASK_OUTGOING_ASSIGNMENT_REQUESTS]?.tasks ?? [],
        columns: outgoingAssignmentRequestsColumns,
        dataTestIds: {
          container: "table_outgoing_requests"
        },
        localization: {
          emptyMessageId: "noOutgoingAssignmentRequests"
        }
      }
    }
  ];

  const renderTable = (table) =>
    isLoading ? <TableLoader columnsCounter={table.columns.length} showHeader /> : <Table {...table} />;

  return (
    <>
      <WrapperCard
        dataTestIds={{
          wrapper: "div_my_tasks",
          title: "lbl_my_tasks"
        }}
        title={<FormattedMessage id="myTasks" />}
      >
        <ConditionWrapper condition={isLoading && !hasTaskTypeInUrl} conditionTemplate={<PanelLoader />}>
          <ConditionWrapper
            condition={isEmpty}
            conditionTemplate={
              <Typography align="center">
                <FormattedMessage id="noTasksRequiringYourAttention" />
              </Typography>
            }
          >
            {tasks.map((task) => {
              const { type, text, count, button, table, dataTestId } = task;
              return (
                <ConditionWrapper key={type} condition={count === 0}>
                  <Accordion
                    expanded={expanded[type]}
                    onChange={() => {
                      handleChange(expanded[type] ? undefined : type);
                    }}
                    disableExpandedSpacing
                  >
                    <TasksOverviewListItem
                      dataTestId={dataTestId}
                      button={false}
                      count={count}
                      key={type}
                      type={type}
                      text={text}
                    />
                    <Box>
                      {button && (
                        <Box mb={2} display="flex" justifyContent="flex-end">
                          <Button variant="text" messageId={button.messageId} link={button.link} />
                        </Box>
                      )}
                      {table && renderTable(table)}
                    </Box>
                  </Accordion>
                </ConditionWrapper>
              );
            })}
          </ConditionWrapper>
        </ConditionWrapper>
      </WrapperCard>
    </>
  );
};

MyTasks.propTypes = {
  data: PropTypes.object.isRequired,
  handleChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isEmpty: PropTypes.bool.isRequired,
  hasTaskTypeInUrl: PropTypes.bool.isRequired,
  expanded: PropTypes.object
};

export default MyTasks;
