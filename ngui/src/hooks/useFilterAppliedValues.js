import React from "react";
import { FormattedMessage } from "react-intl";

export const useFilterAppliedValues = (filters) =>
  filters.flatMap((filter) =>
    filter.appliedFilters.values.map((appliedFilter) => ({
      name: filter.queryKey,
      displayedName: <FormattedMessage id={filter.messageId} />,
      value: appliedFilter.value,
      displayedValue: appliedFilter.renderDisplayedValue()
    }))
  );
