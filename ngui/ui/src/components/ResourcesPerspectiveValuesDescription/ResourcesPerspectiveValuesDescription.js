import React from "react";
import { Stack } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import SubTitle from "components/SubTitle";
import { breakdowns } from "hooks/useBreakdownBy";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";

const getBreakdownByRenderData = (breakdownBy) => ({
  controlName: "categorizeBy",
  renderValue: () => breakdowns.find((breakdown) => breakdown.value === breakdownBy)?.name ?? null
});

const getGroupByRenderData = (groupBy) => ({
  controlName: "groupBy",
  renderValue: () => {
    if (!groupBy.groupType) {
      return <FormattedMessage id="none" />;
    }
    if (groupBy.groupType === "tag") {
      return <KeyValueLabel messageId={groupBy.groupType} value={groupBy.groupBy} />;
    }
    return <FormattedMessage id={groupBy.groupType} />;
  }
});

const getBreakdownStateValueRenderer = (name) =>
  ({
    breakdownBy: getBreakdownByRenderData,
    groupBy: getGroupByRenderData
  }[name] ?? (() => null));

const ResourcesPerspectiveValuesDescription = ({ breakdownBy, breakdownData = {}, filters = [] }) => (
  <Stack spacing={SPACING_1}>
    <KeyValueLabel messageId="breakdownBy" value={<FormattedMessage id={breakdownBy} />} />
    {Object.entries(breakdownData)
      .map(([name, value]) => {
        const renderer = getBreakdownStateValueRenderer(name);

        return renderer(value);
      })
      .filter(Boolean)
      .map(({ controlName, renderValue }) => (
        <KeyValueLabel key={controlName} messageId={controlName} value={renderValue()} />
      ))}
    <div>
      {isEmptyArray(filters) ? (
        <KeyValueLabel messageId="filters" value="-" />
      ) : (
        <>
          <SubTitle>
            <FormattedMessage id="filters" />
          </SubTitle>
          {filters.map(({ name, displayedName, displayedValue }) => (
            <KeyValueLabel key={name} text={displayedName} value={displayedValue} />
          ))}
        </>
      )}
    </div>
  </Stack>
);

ResourcesPerspectiveValuesDescription.propTypes = {
  breakdownBy: PropTypes.oneOf(["tags", "resourceCount", "expenses"]).isRequired,
  breakdownData: PropTypes.shape({
    breakdownBy: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES),
    groupBy: PropTypes.shape({
      groupBy: PropTypes.string,
      groupType: PropTypes.oneOf(["owner", "pool", "tag"])
    })
  }),
  filters: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      displayedName: PropTypes.node,
      displayedValue: PropTypes.node
    })
  )
};

export default ResourcesPerspectiveValuesDescription;
