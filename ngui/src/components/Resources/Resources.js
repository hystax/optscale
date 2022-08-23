import React, { useEffect, useState } from "react";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import ExpensesFilters from "components/ExpensesFilters";
import LinearSelector from "components/LinearSelector";
import PageContentWrapper from "components/PageContentWrapper";
import TypographyLoader from "components/TypographyLoader";
import WrapperCard from "components/WrapperCard";
import CleanExpensesBreakdownContainer from "containers/CleanExpensesBreakdownContainer";
import ExpensesSummaryContainer from "containers/ExpensesSummaryContainer";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import ResourceCountBreakdownContainer from "containers/ResourceCountBreakdownContainer";
import TagsBreakdownContainer from "containers/TagsBreakdownContainer";
import { CLUSTER_TYPES } from "urls";
import { getLength } from "utils/arrays";
import { DATE_RANGE_TYPE, LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

export const BREAKDOWN_BY_QUERY_PARAMETER_NAME = "breakdownBy";

export const CLEAN_EXPENSES_BREAKDOWN_TYPES = Object.freeze({
  EXPENSES: "expenses",
  RESOURCE_COUNT: "resourceCount",
  TAGS: "tags"
});

const BreakdownLinearSelector = ({ value, items, onChange }) => {
  useEffect(() => {
    updateQueryParams({ [BREAKDOWN_BY_QUERY_PARAMETER_NAME]: value.name });
  }, [value.name]);

  return <LinearSelector value={value} label={<FormattedMessage id="breakdownBy" />} onChange={onChange} items={items} />;
};

const Resources = ({
  startDateTimestamp,
  endDateTimestamp,
  filters,
  filterValues,
  onApply,
  onFilterAdd,
  onFilterDelete,
  onFiltersDelete,
  fromMainMenu,
  requestParams,
  isInScopeOfPageMockup = false,
  isFilterValuesLoading = false
}) => {
  const { [BREAKDOWN_BY_QUERY_PARAMETER_NAME]: breakdownQueryParameter } = getQueryParams();

  // TODO: add render here to the definitions
  // value is obsolete
  const breakdownLinearSelectorItems = [
    {
      name: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
      value: "expenses",
      type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
      dataTestId: "breakdown_ls_item_expenses"
    },
    {
      name: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
      value: "resource_type",
      type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
      dataTestId: "breakdown_ls_item_resource_type"
    },
    {
      name: CLEAN_EXPENSES_BREAKDOWN_TYPES.TAGS,
      value: "tags",
      type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
      dataTestId: "breakdown_ls_item_tags"
    }
  ];

  const [activeBreakdown, setActiveBreakdown] = useState(() => {
    const breakdown = breakdownLinearSelectorItems.find(({ name }) => name === breakdownQueryParameter);

    if (breakdown && !isInScopeOfPageMockup) {
      return {
        name: breakdown.name,
        value: breakdown.value
      };
    }

    const { name, value } = getLength(breakdownLinearSelectorItems) > 0 ? breakdownLinearSelectorItems[0] : {};

    return {
      name,
      value
    };
  });

  const actionBarDefinition = {
    goBack: !fromMainMenu,
    title: {
      messageId: "resources",
      dataTestId: "lbl_resources"
    },
    items: [
      {
        key: "configureClusterTypes",
        icon: <GroupWorkOutlinedIcon fontSize="small" />,
        messageId: "configureClusterTypes",
        type: "button",
        link: CLUSTER_TYPES,
        dataTestId: "btn_configure_cluster_types"
      }
    ]
  };

  const renderExpensesBreakdown = () => <CleanExpensesBreakdownContainer requestParams={requestParams} />;

  const renderResourcesCountBreakdown = () => <ResourceCountBreakdownContainer requestParams={requestParams} />;

  const renderTagsBreakdown = () => <TagsBreakdownContainer requestParams={requestParams} />;

  const renderContent = {
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES]: renderExpensesBreakdown,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT]: renderResourcesCountBreakdown,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.TAGS]: renderTagsBreakdown
  }[activeBreakdown.name];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid direction="row" container spacing={SPACING_2} justifyContent="space-between">
          <Grid item>
            <ExpensesSummaryContainer requestParams={requestParams} />
          </Grid>
          <Grid item>
            <RangePickerFormContainer
              onApply={onApply}
              initialStartDateValue={startDateTimestamp}
              initialEndDateValue={endDateTimestamp}
              rangeType={DATE_RANGE_TYPE.RESOURCES}
              definedRanges={getBasicRangesSet()}
            />
          </Grid>
          <Grid xs={12} item>
            {isFilterValuesLoading ? (
              <TypographyLoader linesCount={1} />
            ) : (
              <ExpensesFilters
                filterValues={filterValues}
                appliedFilters={filters}
                onFilterDelete={onFilterDelete}
                onFiltersDelete={onFiltersDelete}
                onFilterAdd={onFilterAdd}
              />
            )}
          </Grid>
          <Grid xs={12} item>
            <BreakdownLinearSelector
              value={activeBreakdown}
              onChange={isInScopeOfPageMockup ? undefined : ({ name, value }) => setActiveBreakdown({ name, value })}
              items={breakdownLinearSelectorItems}
            />
          </Grid>
          <Grid xs={12} item>
            <WrapperCard>{typeof renderContent === "function" ? renderContent() : null}</WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

Resources.propTypes = {
  filters: PropTypes.object.isRequired,
  filterValues: PropTypes.object.isRequired,
  onApply: PropTypes.func.isRequired,
  onFilterAdd: PropTypes.func.isRequired,
  onFilterDelete: PropTypes.func.isRequired,
  onFiltersDelete: PropTypes.func.isRequired,
  fromMainMenu: PropTypes.bool.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  requestParams: PropTypes.object,
  isInScopeOfPageMockup: PropTypes.bool,
  isFilterValuesLoading: PropTypes.bool
};

export default Resources;
