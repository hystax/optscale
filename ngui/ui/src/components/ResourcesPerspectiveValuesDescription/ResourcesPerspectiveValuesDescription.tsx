import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SubTitle from "components/SubTitle";
import { breakdowns } from "hooks/useBreakdownBy";
import { isEmpty as isEmptyArray } from "utils/arrays";
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
      return <KeyValueLabel keyMessageId={groupBy.groupType} value={groupBy.groupBy} />;
    }
    return <FormattedMessage id={groupBy.groupType} />;
  }
});

const getBreakdownStateValueRenderer = (name) =>
  ({
    breakdownBy: getBreakdownByRenderData,
    groupBy: getGroupByRenderData
  })[name] ?? (() => null);

const ResourcesPerspectiveValuesDescription = ({ breakdownBy, breakdownData = {}, filters = [] }) => (
  <Stack spacing={SPACING_1}>
    <KeyValueLabel keyMessageId="breakdownBy" value={<FormattedMessage id={breakdownBy} />} />
    {Object.entries(breakdownData)
      .map(([name, value]) => {
        const renderer = getBreakdownStateValueRenderer(name);

        return renderer(value);
      })
      .filter(Boolean)
      .map(({ controlName, renderValue }) => (
        <KeyValueLabel key={controlName} keyMessageId={controlName} value={renderValue()} />
      ))}
    <div>
      {isEmptyArray(filters) ? (
        <KeyValueLabel keyMessageId="filters" value="-" />
      ) : (
        <>
          <SubTitle>
            <FormattedMessage id="filters" />
          </SubTitle>
          {filters.map(({ name, displayedName, displayedValue }) => (
            <KeyValueLabel key={name} keyText={displayedName} value={displayedValue} />
          ))}
        </>
      )}
    </div>
  </Stack>
);

export default ResourcesPerspectiveValuesDescription;
