import React, { useState, useEffect } from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Accordion from "components/Accordion";
import CleanExpensesTable from "components/CleanExpensesTable";
import FormattedMoney from "components/FormattedMoney";
import { getQueryParams, removeQueryParam, updateQueryParams } from "utils/network";

const GROUP_VALUE_QUERY_PARAM_NAME = "groupValue";

const GroupedTables = ({
  groupedResources,
  onAccordionChange,
  getGroupHeaderDataTestId,
  startDateTimestamp,
  endDateTimestamp
}) => {
  const [expanded, setExpanded] = useState({});
  const toggleExpanded = (groupValue, state) => {
    const closeAll = (currentState) => Object.fromEntries(Object.keys(currentState).map((name) => [name, false]));
    setExpanded((currentState) => ({
      ...closeAll(currentState),
      [groupValue]: state
    }));
  };

  useEffect(() => {
    const getDefaultExpandedState = () => Object.fromEntries(groupedResources.map(([groupValue]) => [groupValue, false]));
    const defaultExpandedState = getDefaultExpandedState();

    const { [GROUP_VALUE_QUERY_PARAM_NAME]: groupValueQueryParam = "" } = getQueryParams();

    const validateGroupValueQueryParam = () => {
      const accordionValues = Object.keys(defaultExpandedState);
      return accordionValues.includes(groupValueQueryParam);
    };

    if (groupValueQueryParam && validateGroupValueQueryParam()) {
      const defaultExpandedStateInitializedWithQueryParameter = Object.fromEntries(
        Object.entries(defaultExpandedState).map(([groupValue]) => [groupValue, groupValue === groupValueQueryParam])
      );
      setExpanded(defaultExpandedStateInitializedWithQueryParameter);
    } else {
      setExpanded(defaultExpandedState);
    }

    // cleans up groupValue before running the effects next time
    // usage: remove groupValue when we group by another value
    return () => removeQueryParam(GROUP_VALUE_QUERY_PARAM_NAME);
  }, [groupedResources]);

  const separator = <div>&nbsp;-&nbsp;</div>;
  const renderTitle = ({ name, count, totalExpenses }) => (
    <Typography style={{ justifyContent: "center", display: "flex" }}>
      <strong>{name}</strong>
      {separator}
      {<FormattedMessage id="resourcesPlural" values={{ count }} />}
      {separator}
      <FormattedMoney value={totalExpenses} />
    </Typography>
  );

  const renderCleanExpensesTable = (expenses, { assignmentRuleCreationQueryParameters }) => (
    <CleanExpensesTable
      startDateTimestamp={startDateTimestamp}
      endDateTimestamp={endDateTimestamp}
      disableColumnsSelection
      expenses={expenses}
      assignmentRuleCreationLinkParameters={assignmentRuleCreationQueryParameters}
    />
  );

  return groupedResources.map(
    ([groupValue, { displayedGroupName, count, totalExpenses, expenses, assignmentRuleCreationQueryParameters }], index) => {
      const isExpanded = !!expanded[groupValue]; // expanded.key undefined on the mount
      return (
        <Accordion
          key={groupValue}
          expanded={isExpanded}
          onChange={(_, expandedAccordionState) => {
            toggleExpanded(groupValue, expandedAccordionState);
            // override query param on open
            if (expandedAccordionState) {
              updateQueryParams({
                [GROUP_VALUE_QUERY_PARAM_NAME]: groupValue
              });
            } else {
              // remove query param on close
              removeQueryParam(GROUP_VALUE_QUERY_PARAM_NAME);
            }
            if (typeof onAccordionChange === "function") {
              onAccordionChange();
            }
          }}
          headerDataTestId={typeof getGroupHeaderDataTestId === "function" ? getGroupHeaderDataTestId(index) : undefined}
        >
          {renderTitle({ name: displayedGroupName, count, totalExpenses })}
          {isExpanded && renderCleanExpensesTable(expenses, { assignmentRuleCreationQueryParameters })}
        </Accordion>
      );
    }
  );
};

GroupedTables.propTypes = {
  groupedResources: PropTypes.arrayOf(
    PropTypes.arrayOf(
      PropTypes.oneOfType([
        PropTypes.string.isRequired,
        PropTypes.shape({
          displayedGroupName: PropTypes.node.isRequired,
          count: PropTypes.number.isRequired,
          totalExpenses: PropTypes.number.isRequired,
          expenses: PropTypes.array.isRequired
        })
      ]).isRequired
    ).isRequired
  ),
  getGroupHeaderDataTestId: PropTypes.oneOfType([PropTypes.func, PropTypes.string]),
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number
};

export default GroupedTables;
