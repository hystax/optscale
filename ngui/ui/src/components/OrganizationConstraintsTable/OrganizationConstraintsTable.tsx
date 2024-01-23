import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormattedMessage } from "react-intl";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import AnomaliesFilters from "components/AnomaliesFilters";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import { useMoneyFormatter } from "components/FormattedMoney";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiData } from "hooks/useApiData";
import { intl } from "translations/react-intl-config";
import { isEmpty } from "utils/arrays";
import { organizationConstraintName, organizationConstraintStatus } from "utils/columns";
import {
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  EXPIRING_BUDGET_POLICY,
  ANOMALY_TYPES,
  TAGGING_POLICY,
  EMPTY_UUID,
  FORMATTED_MONEY_TYPES
} from "utils/constants";
import { formatUTC } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

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

const OrganizationConstraintsTable = ({ constraints, addButtonLink, isLoading = false }) => {
  const isManageResourcesAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });
  const formatter = useMoneyFormatter();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

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
      organizationConstraintName(),
      organizationConstraintStatus(),
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

export default OrganizationConstraintsTable;
