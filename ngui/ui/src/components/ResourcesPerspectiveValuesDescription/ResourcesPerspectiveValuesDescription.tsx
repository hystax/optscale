import React from "react";
import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import ResourcesPerspectiveFilters from "components/ResourcesPerspectiveFilters";
import { breakdowns } from "hooks/useBreakdownBy";
import { CLEAN_EXPENSES_BREAKDOWN_TYPES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { getMetaFormattedName } from "utils/metadata";
import {
  ResourcesPerspectiveValuesDescriptionProps,
  BreakdownData,
  MetaBreakdownData,
  ResourceCountBreakdownData,
  RenderDataItem,
  ExpensesBreakdownData,
} from "./types";

const getExpensesBreakdownByRenderData = ({ breakdownBy, groupBy }: ExpensesBreakdownData): RenderDataItem[] => [
  {
    controlName: "categorizeBy",
    renderValue: () => breakdowns.find((breakdown) => breakdown.value === breakdownBy)?.name ?? null,
  },
  {
    controlName: "groupBy",
    renderValue: () => {
      if (!groupBy || !groupBy.groupType) {
        return <FormattedMessage id="none" />;
      }
      if (groupBy.groupType === "tag") {
        return <KeyValueLabel keyMessageId={groupBy.groupType} value={groupBy.groupBy} />;
      }
      return <FormattedMessage id={groupBy.groupType} />;
    },
  },
];

const getResourceCountBreakdownByRenderData = ({ breakdownBy }: ResourceCountBreakdownData): RenderDataItem[] => [
  {
    controlName: "categorizeBy",
    renderValue: () => breakdowns.find((breakdown) => breakdown.value === breakdownBy)?.name ?? null,
  },
];

const getMetaBreakdownByRenderData = ({ breakdownBy }: MetaBreakdownData): RenderDataItem[] => [
  {
    controlName: "categorizeBy",
    renderValue: () => getMetaFormattedName(breakdownBy),
  },
];

const getBreakdownStateValueRendererByType = (name: string): ((data: BreakdownData) => RenderDataItem[]) =>
  ({
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES]: getExpensesBreakdownByRenderData,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT]: getResourceCountBreakdownByRenderData,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.TAGS]: () => [],
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.META]: getMetaBreakdownByRenderData,
  })[name] ?? (() => []);

const ResourcesPerspectiveValuesDescription = ({
  breakdownBy,
  breakdownData,
  perspectiveFilterValues = {},
  perspectiveAppliedFilters = {},
}: ResourcesPerspectiveValuesDescriptionProps) => (
  <Stack spacing={SPACING_1}>
    <KeyValueLabel keyMessageId="breakdownBy" value={<FormattedMessage id={breakdownBy} />} />
    {getBreakdownStateValueRendererByType(breakdownBy)(breakdownData)
      .filter(Boolean)
      .map(({ controlName, renderValue }) => (
        <KeyValueLabel key={controlName} keyMessageId={controlName} value={renderValue()} />
      ))}
    <ResourcesPerspectiveFilters
      perspectiveFilterValues={perspectiveFilterValues}
      perspectiveAppliedFilters={perspectiveAppliedFilters}
    />
  </Stack>
);

export default ResourcesPerspectiveValuesDescription;
