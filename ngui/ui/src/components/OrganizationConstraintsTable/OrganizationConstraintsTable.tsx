import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import ExpandableList from "components/ExpandableList";
import { FILTER_TYPE } from "components/FilterComponents/constants";
import { useMoneyFormatter } from "components/FormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { useIsAllowed } from "hooks/useAllowedActions";
import { intl } from "translations/react-intl-config";
import { isEmptyArray } from "utils/arrays";
import { organizationConstraintName, organizationConstraintStatus } from "utils/columns";
import {
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  EXPIRING_BUDGET_POLICY,
  ANOMALY_TYPES,
  TAGGING_POLICY,
  EMPTY_UUID,
  FORMATTED_MONEY_TYPES,
} from "utils/constants";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { getResourcesLink } from "utils/organizationConstraints/getResourcesLink";
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
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>),
      }
    );
  }

  if (type === QUOTA_POLICY) {
    const { max_value: maxValue } = definition;
    return intl.formatMessage(
      { id: "quotaPolicyDescription" },
      {
        value: maxValue,
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>),
      }
    );
  }

  if (type === RECURRING_BUDGET_POLICY) {
    const { monthly_budget: monthlyBudget } = definition;
    return intl.formatMessage(
      { id: "recurringBudgetPolicyDescription" },
      {
        budget: formatter(FORMATTED_MONEY_TYPES.COMMON, monthlyBudget),
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>),
      }
    );
  }

  if (type === EXPIRING_BUDGET_POLICY) {
    const { total_budget: totalBudget, start_date: startDate } = definition;
    return intl.formatMessage(
      { id: "expiringBudgetPolicyDescription" },
      {
        budget: formatter(FORMATTED_MONEY_TYPES.COMMON, totalBudget),
        startDate: format(secondsToMilliseconds(startDate), EN_FULL_FORMAT),
        strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>),
      }
    );
  }

  if (type === TAGGING_POLICY) {
    const {
      conditions: { tag: prohibitedTag, without_tag: requiredTag },
      start_date: startDate,
    } = definition;

    const commonValues = {
      startDate: format(secondsToMilliseconds(startDate), EN_FULL_FORMAT),
      strong: (chunks) => (rawString ? chunks : <strong>{chunks}</strong>),
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
  const navigate = useNavigate();

  const isManageResourcesAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });
  const formatter = useMoneyFormatter();

  const dataSources = useAllDataSources();

  const tableData = useMemo(
    () =>
      constraints.map((constraint) => {
        const { filters } = constraint;

        const filterDefinitions = Object.values(FILTER_CONFIGS).flatMap((config) => {
          if (config.type === FILTER_TYPE.SELECTION) {
            const appliedFilters = filters[config.apiName] ?? [];

            if (isEmptyArray(appliedFilters)) {
              return [];
            }

            return appliedFilters.map((appliedFilter) => {
              const value = config.transformers.getValue(appliedFilter);

              return {
                displayedName: config.label,
                displayedValue: config.renderPerspectiveItem(value, appliedFilters),
                displayedNameString: config.labelString,
                displayedValueString: config.renderPerspectiveItem(value, appliedFilters, { stringify: true }),
              };
            });
          }

          if (config.type === FILTER_TYPE.RANGE) {
            const from = filters[config.fromApiName];
            const to = filters[config.toApiName];

            if (!from && !to) {
              return [];
            }

            return [
              {
                displayedName: config.label,
                displayedValue: config.renderPerspectiveItem({ from, to }),
                displayedNameString: config.labelString,
                displayedValueString: config.renderPerspectiveItem({ from, to }),
              },
            ];
          }

          return [];
        });

        return {
          ...constraint,
          filterDefinitions,
          descriptionForSearch: buildDescription({
            type: constraint.type,
            definition: constraint.definition,
            formatter,
            rawString: true,
          }),
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
        enableSorting: false,
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_filters">
            <FormattedMessage id="filters" />
          </TextWithDataTestId>
        ),
        id: "filters",
        accessorFn: (originalRow) =>
          originalRow.filterDefinitions
            .map(({ displayedNameString, displayedValueString }) => `${displayedNameString}: ${displayedValueString}`)
            .join(" "),
        cell: ({ row: { original } }) => {
          const { filterDefinitions } = original;

          return isEmptyArray(filterDefinitions) ? (
            CELL_EMPTY_VALUE
          ) : (
            <ExpandableList
              items={filterDefinitions}
              render={({ displayedNameString, displayedValueString, displayedName, displayedValue }) => (
                <KeyValueLabel
                  key={`${displayedNameString}-${displayedValueString}`}
                  keyText={displayedName}
                  value={displayedValue}
                />
              )}
              maxRows={5}
            />
          );
        },
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        enableSorting: false,
        id: "actions",
        cell: ({ row: { original, index } }) => (
          <IconButton
            dataTestId={`actions_column_link_${index}`}
            icon={<ListAltOutlinedIcon />}
            onClick={() => {
              const link = getResourcesLink(original);
              navigate(link);
            }}
            tooltip={{
              show: true,
              value: <FormattedMessage id="showResources" />,
            }}
          />
        ),
      },
    ],
    [formatter, navigate]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table
      actionBar={{
        show: isManageResourcesAllowed && !isEmptyArray(dataSources),
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
              dataTestId: "btn_add",
            },
          ],
        },
      }}
      data={tableData}
      columns={columns}
      withSearch
      dataTestIds={{
        searchInput: "input_search",
        searchButton: "btn_search",
        deleteSearchButton: "btn_delete_search",
      }}
      localization={{ emptyMessageId: "noPolicies" }}
      pageSize={50}
    />
  );
};

export default OrganizationConstraintsTable;
