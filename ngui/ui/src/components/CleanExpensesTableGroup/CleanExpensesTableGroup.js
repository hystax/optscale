import React, { useState, useMemo, useEffect, useCallback } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch, useSelector } from "react-redux";
import CleanExpensesTable from "components/CleanExpensesTable";
import GroupedTables from "components/GroupedTables";
import LinearSelector from "components/LinearSelector";
import PoolLabel from "components/PoolLabel";
import { useReactiveSearchParams } from "hooks/useReactiveSearchParams";
import { intl } from "translations/react-intl-config";
import { GROUP_BY_PARAM_NAME, GROUP_TYPE_PARAM_NAME } from "urls";
import { createGroupsObjectFromArray, getLength, isEmpty as isEmptyArray } from "utils/arrays";
import {
  LINEAR_SELECTOR_ITEMS_TYPES,
  CLEAN_EXPENSES_GROUP_TYPES,
  ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER,
  TAG_IS,
  CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX,
  CLEAN_EXPENSES_GROUP_TYPES_LIST
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { updateQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";
import { getPaginationQueryKey, getSearchQueryKey } from "utils/tables";
import { TOTAL_EXPENSES, COUNT } from "./constant";
import SortGroupsBySelector from "./SortGroupsBySelector";
import { changeSortGroupsBy } from "./SortGroupsBySelector/actionCreators";
import { RESOURCES_SORT_GROUPS_BY } from "./SortGroupsBySelector/reducer";

const DEFAULT_GROUP_STATE = {};

const OTHER_TAG_GROUP_VALUE = "other";
const EMPTY_GROUP_VALUE = "";

const getUniqueTags = (expenses) => [...new Set(expenses.map((expense) => Object.keys(expense.tags || {})).flat())].sort();

const getGroupedExpenses = ({ expenses, groupType, groupBy, sortGroupsBy }) => {
  const groupByIteratee = {
    [CLEAN_EXPENSES_GROUP_TYPES.POOL]: (expense) => expense.pool?.id ?? EMPTY_GROUP_VALUE,
    [CLEAN_EXPENSES_GROUP_TYPES.OWNER]: (expense) => expense.owner?.id ?? EMPTY_GROUP_VALUE,
    [CLEAN_EXPENSES_GROUP_TYPES.TAG]: (expense) => {
      const tag = expense.tags?.[groupBy];

      // tag value can be empty, for example, «marketing: ''»,
      if (tag === "") {
        return EMPTY_GROUP_VALUE;
      }
      return tag ?? OTHER_TAG_GROUP_VALUE;
    }
  }[groupType];

  const sortGroups = (groups) => [
    // in desc order
    ...groups.sort((a, b) => {
      const aTotalExpenses = a[1][sortGroupsBy];
      const bTotalExpenses = b[1][sortGroupsBy];

      return bTotalExpenses - aTotalExpenses;
    })
  ];

  const getEmptyDisplayedMessageId = () =>
    ({
      [CLEAN_EXPENSES_GROUP_TYPES.TAG]: "(empty)"
    }[groupType]);

  const getAssignmentRuleCreationQueryParameters = (groupValue) => {
    if (groupType === CLEAN_EXPENSES_GROUP_TYPES.TAG && ![OTHER_TAG_GROUP_VALUE, EMPTY_GROUP_VALUE].includes(groupValue)) {
      return {
        [ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER]: [
          {
            type: TAG_IS,
            value: {
              tagKey: groupBy,
              tagValue: groupValue
            }
          }
        ]
      };
    }

    return undefined;
  };

  const getDisplayedGroupName = (groupValue, expense) => {
    if (groupValue === EMPTY_GROUP_VALUE) {
      return intl.formatMessage({ id: getEmptyDisplayedMessageId() });
    }

    const groupNameGetter = {
      [CLEAN_EXPENSES_GROUP_TYPES.POOL]: () => {
        const {
          pool: { name, purpose: type, id }
        } = expense;
        return <PoolLabel name={name} type={type} id={id} disableLink />;
      },
      [CLEAN_EXPENSES_GROUP_TYPES.OWNER]: () => expense.owner.name,
      [CLEAN_EXPENSES_GROUP_TYPES.TAG]: () =>
        groupValue === OTHER_TAG_GROUP_VALUE ? intl.formatMessage({ id: groupValue }) : groupValue
    }[groupType];

    return groupNameGetter();
  };

  const getTotalExpenses = (groupData) => groupData.reduce((result, expense) => result + expense.cost || 0, 0);

  const groupedExpenses = Object.entries(createGroupsObjectFromArray(expenses, groupByIteratee)).map(
    ([groupValue, groupData]) => [
      groupValue,
      {
        displayedGroupName: getDisplayedGroupName(groupValue, groupData[0]),
        expenses: groupData,
        [TOTAL_EXPENSES]: getTotalExpenses(groupData),
        [COUNT]: getLength(groupData),
        assignmentRuleCreationQueryParameters: getAssignmentRuleCreationQueryParameters(groupValue)
      }
    ]
  );

  const sortedGroups = isEmptyArray(groupedExpenses) ? groupedExpenses : sortGroups(groupedExpenses);

  return sortedGroups;
};

const validateGroupTypeQueryParameter = (groupType) => CLEAN_EXPENSES_GROUP_TYPES_LIST.includes(groupType);
const validateGroupByQueryParameter = (groupBy, { tags }) => tags.includes(groupBy);

const SEARCH_PARAMS = [GROUP_TYPE_PARAM_NAME, GROUP_BY_PARAM_NAME];

const CleanExpensesTableGroup = ({
  expenses,
  downloadResources,
  isDownloadingResources = false,
  startDateTimestamp,
  endDateTimestamp
}) => {
  const {
    [GROUP_TYPE_PARAM_NAME]: groupTypeQueryParameter = "",
    [GROUP_BY_PARAM_NAME]: groupByQueryParameter = groupTypeQueryParameter
  } = useReactiveSearchParams(SEARCH_PARAMS);

  const dispatch = useDispatch();

  const tags = useMemo(() => getUniqueTags(expenses), [expenses]);

  const validateQueryParameters = useCallback(() => {
    const isGroupTypeQueryParameterValid = validateGroupTypeQueryParameter(groupTypeQueryParameter);
    const isGroupByQueryParameterValid =
      groupTypeQueryParameter === CLEAN_EXPENSES_GROUP_TYPES.TAG
        ? validateGroupByQueryParameter(groupByQueryParameter, { tags })
        : true;

    return isGroupTypeQueryParameterValid && isGroupByQueryParameterValid;
  }, [groupByQueryParameter, groupTypeQueryParameter, tags]);

  const sortGroupsBy = useSelector((state) => state[RESOURCES_SORT_GROUPS_BY]);
  const setSortGroupsBy = (value) => {
    dispatch(changeSortGroupsBy(value));
  };

  const [cachedGroups, setCachedGroups] = useState({});

  useEffect(() => {
    if (validateQueryParameters()) {
      setCachedGroups((cache) => ({
        ...cache,
        [groupByQueryParameter]: getGroupedExpenses({
          expenses,
          groupType: groupTypeQueryParameter,
          groupBy: groupByQueryParameter,
          sortGroupsBy
        })
      }));
    }
  }, [expenses, groupByQueryParameter, groupTypeQueryParameter, sortGroupsBy, validateQueryParameters]);

  const groupState = validateQueryParameters()
    ? {
        groupType: groupTypeQueryParameter,
        groupBy: groupByQueryParameter
      }
    : DEFAULT_GROUP_STATE;

  const handleGroupSelectorChange = ({ groupType, groupBy }) => {
    if (!cachedGroups[groupBy]) {
      setCachedGroups((cache) => ({
        ...cache,
        [groupBy]: getGroupedExpenses({ expenses, groupType, groupBy, sortGroupsBy })
      }));
    }
  };

  const isGroupStateEmpty = isEmptyObject(groupState);

  return (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
        <Box display="flex">
          <LinearSelector
            value={
              isGroupStateEmpty
                ? {}
                : {
                    name: groupState.groupType,
                    value: groupState.groupBy
                  }
            }
            label={<FormattedMessage id="groupBy" />}
            onChange={({ name: groupType, value: groupBy }) => {
              updateQueryParams({
                [getPaginationQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined,
                [getSearchQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined,
                [GROUP_TYPE_PARAM_NAME]: groupType,
                [GROUP_BY_PARAM_NAME]: groupBy
              });
              handleGroupSelectorChange({
                groupType,
                groupBy
              });
            }}
            onClear={() => {
              updateQueryParams({
                [GROUP_TYPE_PARAM_NAME]: undefined,
                [GROUP_BY_PARAM_NAME]: undefined,
                [getPaginationQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined,
                [getSearchQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined
              });
            }}
            items={[
              {
                name: CLEAN_EXPENSES_GROUP_TYPES.POOL,
                value: CLEAN_EXPENSES_GROUP_TYPES.POOL,
                type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
                dataTestId: "ls_item_pool"
              },
              {
                name: CLEAN_EXPENSES_GROUP_TYPES.OWNER,
                value: CLEAN_EXPENSES_GROUP_TYPES.OWNER,
                type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
                dataTestId: "ls_item_owner"
              },
              ...(!isEmptyArray(tags)
                ? [
                    {
                      name: CLEAN_EXPENSES_GROUP_TYPES.TAG,
                      type: LINEAR_SELECTOR_ITEMS_TYPES.POPOVER,
                      dataTestId: "ls_item_tag",
                      items: tags.map((tag, index) => ({
                        name: CLEAN_EXPENSES_GROUP_TYPES.TAG,
                        value: tag,
                        label: tag,
                        key: tag,
                        dataTestId: `ls_mi_tag_name_${index}`
                      }))
                    }
                  ]
                : [])
            ]}
            dataTestIds={{
              label: "ls_lbl_group"
            }}
          />
          {!isGroupStateEmpty && <SortGroupsBySelector sortGroupsBy={sortGroupsBy} setSortGroupsBy={setSortGroupsBy} />}
        </Box>
      </Grid>
      <Grid item xs={12} style={{ paddingTop: 0 }}>
        {!isGroupStateEmpty ? (
          <GroupedTables
            startDateTimestamp={startDateTimestamp}
            endDateTimestamp={endDateTimestamp}
            onAccordionChange={() => {
              updateQueryParams({
                [getPaginationQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined,
                [getSearchQueryKey(CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX)]: undefined
              });
            }}
            groupedResources={cachedGroups[groupState.groupBy] ?? []}
            getGroupHeaderDataTestId={(index) => `group_${groupState.groupType}_${index}`}
          />
        ) : (
          <CleanExpensesTable
            startDateTimestamp={startDateTimestamp}
            endDateTimestamp={endDateTimestamp}
            expenses={expenses}
            downloadResources={downloadResources}
            isDownloadingResources={isDownloadingResources}
          />
        )}
      </Grid>
    </Grid>
  );
};

CleanExpensesTableGroup.propTypes = {
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  expenses: PropTypes.array,
  downloadResources: PropTypes.func,
  isDownloadingResources: PropTypes.bool
};

export default CleanExpensesTableGroup;
