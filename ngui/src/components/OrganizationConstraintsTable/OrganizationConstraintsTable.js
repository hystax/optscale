import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import AnomaliesFilters from "components/AnomaliesFilters";
import AnomalyRunChartCell from "components/AnomalyRunChartCell";
import CaptionedCell from "components/CaptionedCell";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import ProgressBar from "components/ProgressBar";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiData } from "hooks/useApiData";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { intl } from "translations/react-intl-config";
import { getAnomalyUrl, getQuotaAndBudgetUrl, getTaggingPolicyUrl } from "urls";
import { isEmpty } from "utils/arrays";
import {
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  EXPIRING_BUDGET_POLICY,
  ANOMALY_TYPES,
  TAGGING_POLICY,
  EMPTY_UUID,
  TAGGING_POLICY_TYPES,
  QUOTAS_AND_BUDGETS_TYPES,
  FORMATTED_MONEY_TYPES
} from "utils/constants";
import { formatUTC } from "utils/datetime";
import { getPoolColorStatus } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";
import SlicedText from "../SlicedText";
import useStyles from "./OrganizationConstraintsTable.styles";

const buildDescription = (type, definition) => {
  if (ANOMALY_TYPES[type]) {
    const { threshold, threshold_days: period } = definition;
    return (
      <FormattedMessage
        id="anomalyPolicyDescription"
        values={{
          sentenceType: intl.formatMessage({ id: ANOMALY_TYPES[type] }).toLowerCase(),
          period,
          threshold,
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    );
  }

  if (type === QUOTA_POLICY) {
    const { max_value: maxValue } = definition;
    return (
      <FormattedMessage
        id="quotaPolicyDescription"
        values={{
          value: maxValue,
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    );
  }

  if (type === RECURRING_BUDGET_POLICY) {
    const { monthly_budget: monthlyBudget } = definition;
    return (
      <FormattedMessage
        id="recurringBudgetPolicyDescription"
        values={{
          budget: <FormattedMoney value={monthlyBudget} />,
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    );
  }

  if (type === EXPIRING_BUDGET_POLICY) {
    const { total_budget: totalBudget, start_date: startDate } = definition;
    return (
      <FormattedMessage
        id="expiringBudgetPolicyDescription"
        values={{
          budget: <FormattedMoney value={totalBudget} />,
          startDate: formatUTC(startDate),
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    );
  }

  if (type === TAGGING_POLICY) {
    const {
      conditions: { tag: prohibitedTag, without_tag: requiredTag },
      start_date: startDate
    } = definition;

    const commonValues = { startDate: formatUTC(startDate), strong: (chunks) => <strong>{chunks}</strong> };

    if (prohibitedTag === EMPTY_UUID) {
      return <FormattedMessage id="taggingPolicy.anyTags" values={commonValues} />;
    }

    if (!prohibitedTag) {
      return <FormattedMessage id="taggingPolicy.requiredTagDescription" values={{ requiredTag, ...commonValues }} />;
    }

    if (!requiredTag) {
      return <FormattedMessage id="taggingPolicy.prohibitedTagDescription" values={{ prohibitedTag, ...commonValues }} />;
    }

    return (
      <FormattedMessage
        id="taggingPolicy.tagsCorrelationDescription"
        values={{ firstTag: prohibitedTag, secondTag: requiredTag, ...commonValues }}
      />
    );
  }

  return null;
};

const getLink = (id, type) => {
  if (ANOMALY_TYPES[type]) {
    return getAnomalyUrl(id);
  }

  if (TAGGING_POLICY_TYPES[type]) {
    return getTaggingPolicyUrl(id);
  }

  return getQuotaAndBudgetUrl(id);
};

const ConstraintStatusCell = ({ lastRun, lastRunResult, type, definition }) => {
  const { classes } = useStyles();

  if (lastRun === 0 || isEmptyObject(lastRunResult)) {
    return <FormattedMessage id="noStatusInformationYet" />;
  }

  if (ANOMALY_TYPES[type]) {
    const { breakdown = {}, average = 0, today = 0 } = lastRunResult;

    return (
      <AnomalyRunChartCell breakdown={breakdown} today={today} average={average} threshold={definition.threshold} type={type} />
    );
  }

  if (QUOTAS_AND_BUDGETS_TYPES[type]) {
    const { current, limit } = lastRunResult;
    const xDividedByY = current / limit;
    const percent = xDividedByY * 100;

    const label = type === QUOTA_POLICY ? current : <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={current} />;
    return (
      <ProgressBar color={getPoolColorStatus(percent)} value={percent} width="160px">
        {label}
      </ProgressBar>
    );
  }

  // and for TAGGING_POLICY_TYPES[type]
  const { value: violations } = lastRunResult;

  return (
    <div className={classes.centered}>
      {violations === 0 ? (
        <CheckCircleIcon fontSize="small" color="success" />
      ) : (
        <>
          <CancelIcon fontSize="small" color="error" />
          <FormattedMessage id="violationsRightNow" values={{ value: violations }} />
        </>
      )}
    </div>
  );
};

const OrganizationConstraintsTable = ({ constraints, addButtonLink, isLoading = false }) => {
  const isManageResourcesAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const memoizedClusterTypes = useMemo(() => constraints, [constraints]);

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessor: "name",
        Cell: ({
          row: {
            original: { id, type, last_run: lastRun, limit_hits: limitHits = [] }
          },
          cell: { value }
        }) => {
          const timeAgo = useIntervalTimeAgo(lastRun, 1);
          const hitsNum = limitHits.length;
          return (
            <CaptionedCell
              caption={{
                key: "lastRunCaption",
                node: lastRun ? (
                  <IconLabel
                    icon={
                      hitsNum !== 0 && (
                        <Tooltip title={intl.formatMessage({ id: "hitsForLastDays" }, { value: hitsNum, amount: 3 })}>
                          <ErrorOutlineIcon fontSize="inherit" />
                        </Tooltip>
                      )
                    }
                    label={<KeyValueLabel variant="caption" messageId="lastCheck" value={timeAgo} />}
                    component={RouterLink}
                  />
                ) : null
              }}
            >
              <Link to={getLink(id, type)} component={RouterLink}>
                <SlicedText limit={40} text={value} />
              </Link>
            </CaptionedCell>
          );
        },
        defaultSort: "asc"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        id: "status",
        Cell: ({
          row: {
            original: { last_run: lastRun, last_run_result: lastRunResult = {}, definition, type }
          }
        }) => <ConstraintStatusCell lastRun={lastRun} lastRunResult={lastRunResult} type={type} definition={definition} />,
        disableSortBy: true
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_description">
            <FormattedMessage id="description" />
          </TextWithDataTestId>
        ),
        accessor: "type",
        Cell: ({ row: { original: { type, definition } = {} } }) => buildDescription(type, definition),
        disableSortBy: true
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_filters">
            <FormattedMessage id="filters" />
          </TextWithDataTestId>
        ),
        accessor: "filters",
        disableSortBy: true,
        Cell: ({ cell: { value } }) => (isEmptyObject(value) ? CELL_EMPTY_VALUE : <AnomaliesFilters filters={value} />)
      }
    ],
    []
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <>
      <Table
        actionBar={{
          show: isManageResourcesAllowed && !isEmpty(cloudAccounts),
          definition: {
            items: [
              {
                key: "add",
                icon: <AddOutlinedIcon fontSize="small" />,
                messageId: "add",
                color: "success",
                variant: "contained",
                type: "button",
                link: addButtonLink,
                dataTestId: "btn_add"
              }
            ]
          }
        }}
        data={memoizedClusterTypes}
        columns={columns}
        dataTestIds={{
          searchInput: "input_search"
        }}
        localization={{ emptyMessageId: "noPolicies" }}
      />
    </>
  );
};

OrganizationConstraintsTable.propTypes = {
  constraints: PropTypes.array.isRequired,
  addButtonLink: PropTypes.string.isRequired,
  isLoading: PropTypes.bool
};

export default OrganizationConstraintsTable;
