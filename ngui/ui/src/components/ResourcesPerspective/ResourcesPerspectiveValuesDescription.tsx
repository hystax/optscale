import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { FILTER_TYPE } from "components/FilterComponents/constants";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import SubTitle from "components/SubTitle";
import { breakdowns } from "hooks/useBreakdownBy";
import { isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { isEmptyObject } from "utils/objects";

const getBreakdownByRenderData = (breakdownBy) => ({
  controlName: "categorizeBy",
  renderValue: () => breakdowns.find((breakdown) => breakdown.value === breakdownBy)?.name ?? null,
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
  },
});

const getBreakdownStateValueRenderer = (name) =>
  ({
    breakdownBy: getBreakdownByRenderData,
    groupBy: getGroupByRenderData,
  })[name] ?? (() => null);

const ResourcesPerspectiveValuesDescription = ({
  breakdownBy,
  breakdownData = {},
  perspectiveFilterValues = {},
  perspectiveAppliedFilters = {},
}) => (
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
      {isEmptyObject(perspectiveFilterValues) ? (
        <KeyValueLabel keyMessageId="filters" value="-" />
      ) : (
        <>
          <SubTitle>
            <FormattedMessage id="filters" />
          </SubTitle>
          {Object.values(FILTER_CONFIGS).map((filterConfig) => {
            if (filterConfig.type === FILTER_TYPE.RANGE) {
              const from = perspectiveAppliedFilters[filterConfig.fromName];
              const to = perspectiveAppliedFilters[filterConfig.toName];

              if (!from && !to) {
                return null;
              }

              return (
                <KeyValueLabel
                  key={filterConfig.id}
                  keyText={filterConfig.label}
                  value={filterConfig.renderPerspectiveItem({ from, to })}
                />
              );
            }

            if (filterConfig.type === FILTER_TYPE.SELECTION) {
              const values = perspectiveAppliedFilters[filterConfig.id];

              if (isEmptyArray(values)) {
                return null;
              }

              return values.map((value) => (
                <KeyValueLabel
                  key={`${filterConfig.id}-${value}`}
                  keyText={filterConfig.label}
                  value={filterConfig.renderPerspectiveItem(value, perspectiveFilterValues[filterConfig.apiName])}
                />
              ));
            }

            return null;
          })}
        </>
      )}
    </div>
  </Stack>
);

export default ResourcesPerspectiveValuesDescription;
