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
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import FormattedMoney, { useMoneyFormatter } from "components/FormattedMoney";
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

const buildDescription = ({ type, definition, formatter, rawString = false }) => {
  if (ANOMALY_TYPES[type]) {
    const { threshold, threshold_days: period } = definition;
    return intl.formatMessage(
      { id: "anomalyPolicyDescription" },
      {
        sentenceType: intl.formatMessage({ id: ANOMALY_TYPES[type] }).toLowerCase(),
        period,
        threshold,
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>)
      }
    );
  }

  if (type === QUOTA_POLICY) {
    const { max_value: maxValue } = definition;
    return intl.formatMessage(
      { id: "quotaPolicyDescription" },
      {
        value: maxValue,
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>)
      }
    );
  }

  if (type === RECURRING_BUDGET_POLICY) {
    const { monthly_budget: monthlyBudget } = definition;
    return intl.formatMessage(
      { id: "recurringBudgetPolicyDescription" },
      {
        budget: formatter(FORMATTED_MONEY_TYPES.COMMON, monthlyBudget),
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>)
      }
    );
  }

  if (type === EXPIRING_BUDGET_POLICY) {
    const { total_budget: totalBudget, start_date: startDate } = definition;
    return intl.formatMessage(
      { id: "expiringBudgetPolicyDescription" },
      {
        budget: formatter(FORMATTED_MONEY_TYPES.COMMON, totalBudget),
        startDate: formatUTC(startDate),
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>)
      }
    );
  }

  if (type === TAGGING_POLICY) {
    const {
      conditions: { tag: prohibitedTag, without_tag: requiredTag },
      start_date: startDate
    } = definition;

    const commonValues = {
      startDate: formatUTC(startDate),
      strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>)
    };

    if (prohibitedTag === EMPTY_UUID) {
      return intl.formatMessage({ id: "taggingPolicy.anyTags" }, commonValues);
    }

    if (!prohibitedTag) {
      return intl.formatMessage({ id: "taggingPolicy.requiredTagDescription" }, { requiredTag, ...commonValues });
    }

    if (!requiredTag) {
      return intl.formatMessage({ id: "taggingPolicy.prohibitedTagDescription" }, { prohibitedTag, ...commonValues });
    }

    return intl.formatMessage(
      { id: "taggingPolicy.tagsCorrelationDescription" },
      { firstTag: prohibitedTag, secondTag: requiredTag, ...commonValues }
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
      <ProgressBar color={getPoolColorStatus(percent)} value={percent} minWidth="160px">
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

const NameCell = ({ lastRun, limitHits, id, type, name }) => {
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
        <SlicedText limit={40} text={name} />
      </Link>
    </CaptionedCell>
  );
};

const OrganizationConstraintsTable = ({ constraints, addButtonLink, isLoading = false }) => {
  const isManageResourcesAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });
  const formatter = useMoneyFormatter();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const memoizedConstraints = useMemo(
    () =>
      constraints.map((constraint) => {
        const filtersResources = new Filters({
          filters: RESOURCE_FILTERS,
          filterValues: constraint.filters
        });
        const filtersString = isEmptyObject(constraint.filters)
          ? ""
          : filtersResources
              .getFilterValuesAsAppliedItems()
              .map(({ displayedNameString, displayedValueString }) => `${displayedNameString}: ${displayedValueString}`)
              .join(" ");

        return {
          ...constraint,
          descriptionForSearch: buildDescription({
            type: constraint.type,
            definition: constraint.definition,
            formatter,
            rawString: true
          }),
          filtersString
        };
      }),
    [constraints, formatter]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({
          row: {
            original: { id, type, last_run: lastRun, limit_hits: limitHits = [] }
          },
          cell
        }) => <NameCell lastRun={lastRun} limitHits={limitHits} id={id} type={type} name={cell.getValue()} />,
        defaultSort: "asc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        id: "status",
        cell: ({
          row: {
            original: { last_run: lastRun, last_run_result: lastRunResult = {}, definition, type }
          }
        }) => <ConstraintStatusCell lastRun={lastRun} lastRunResult={lastRunResult} type={type} definition={definition} />,
        enableSorting: false,
        enableGlobalFilter: false
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_description">
            <FormattedMessage id="description" />
          </TextWithDataTestId>
        ),
        accessorKey: "descriptionForSearch",
        cell: ({ row: { original: { type, definition } = {} } }) => buildDescription({ type, definition, formatter }),
        enableSorting: false
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_filters">
            <FormattedMessage id="filters" />
          </TextWithDataTestId>
        ),
        accessorKey: "filtersString",
        enableSorting: false,
        cell: ({ row: { original: { filters } = {} } }) =>
          isEmptyObject(filters) ? CELL_EMPTY_VALUE : <AnomaliesFilters filters={filters} />
      }
    ],
    [formatter]
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
        data={memoizedConstraints}
        columns={columns}
        withSearch
        dataTestIds={{
          searchInput: "input_search",
          searchButton: "btn_search",
          deleteSearchButton: "btn_delete_search"
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
