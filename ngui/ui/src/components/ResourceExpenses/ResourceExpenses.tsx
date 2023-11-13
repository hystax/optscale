import { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import ButtonGroup from "components/ButtonGroup";
import { getBasicRangesSet, getCustomRange } from "components/DateRangePicker/defaults";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import ResourcePaidNetworkTrafficContainer from "containers/ResourcePaidNetworkTrafficContainer";
import ResourceRawExpensesContainer from "containers/ResourceRawExpensesContainer";
import { useResourceDetailsDefaultDateRange } from "hooks/useResourceDetailsDefaultDateRange";
import { RESOURCE_PAGE_EXPENSES_TABS, DATE_RANGE_FILTERS, DATE_RANGE_TYPE } from "utils/constants";
import { millisecondsToSeconds, performDateTimeFunction, startOfDay, endOfDay, secondsToMilliseconds } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const useActiveExpensesMode = ({ modes, defaultMode }) => {
  const { expensesMode } = getQueryParams();
  const [activeExpensesMode, setActiveExpensesMode] = useState(modes.includes(expensesMode) ? expensesMode : defaultMode);

  useEffect(() => {
    updateQueryParams({ expensesMode: activeExpensesMode });
  }, [activeExpensesMode]);

  return [activeExpensesMode, setActiveExpensesMode];
};

const ExpensesModeButtonGroup = ({ activeExpensesMode, onClick, hasNetworkTrafficExpenses }) => {
  const buttonsGroup = [
    {
      id: RESOURCE_PAGE_EXPENSES_TABS.GROUPED,
      messageId: "grouped",
      action: () => onClick(RESOURCE_PAGE_EXPENSES_TABS.GROUPED),
      dataTestId: "btn_grouped"
    },
    {
      id: RESOURCE_PAGE_EXPENSES_TABS.DETAILED,
      messageId: "detailed",
      action: () => onClick(RESOURCE_PAGE_EXPENSES_TABS.DETAILED),
      dataTestId: "btn_detailed"
    },
    ...(hasNetworkTrafficExpenses
      ? [
          {
            id: RESOURCE_PAGE_EXPENSES_TABS.PAID_NETWORK_TRAFFIC,
            messageId: "paidNetworkTraffic",
            action: () => onClick(RESOURCE_PAGE_EXPENSES_TABS.PAID_NETWORK_TRAFFIC),
            dataTestId: "btn_paid_network_traffic"
          }
        ]
      : [])
  ];

  return (
    <ButtonGroup
      buttons={buttonsGroup}
      activeButtonIndex={buttonsGroup.findIndex((button) => button.id === activeExpensesMode)}
    />
  );
};

const ResourceExpenses = ({ resourceId, firstSeen, lastSeen, hasNetworkTrafficExpenses = false }) => {
  const [startDate, endDate] = useResourceDetailsDefaultDateRange({
    lastSeen,
    firstSeen
  });

  const [activeExpensesMode, setActiveExpensesMode] = useActiveExpensesMode({
    modes: Object.values(RESOURCE_PAGE_EXPENSES_TABS),
    defaultMode: RESOURCE_PAGE_EXPENSES_TABS.GROUPED
  });

  const [requestParams, setRequestParams] = useState({
    startDate,
    endDate
  });

  useEffect(() => {
    updateQueryParams({
      startDate: requestParams.startDate,
      endDate: requestParams.endDate
    });
  }, [requestParams.startDate, requestParams.endDate]);

  const firstSeenStartOfDay = millisecondsToSeconds(
    performDateTimeFunction(startOfDay, true, secondsToMilliseconds(firstSeen))
  );
  const lastSeenEndOfDay = millisecondsToSeconds(performDateTimeFunction(endOfDay, true, secondsToMilliseconds(lastSeen)));

  const applyFilter = ({ startDate: newStartDate, endDate: newEndDate }) => {
    const params = {
      ...requestParams,
      startDate: newStartDate,
      endDate: newEndDate
    };
    setRequestParams(params);
  };

  return (
    <Grid container spacing={SPACING_2} alignItems="center" justifyContent="space-between">
      <Grid item>
        <ExpensesModeButtonGroup
          onClick={(id) => setActiveExpensesMode(id)}
          activeExpensesMode={activeExpensesMode}
          hasNetworkTrafficExpenses={hasNetworkTrafficExpenses}
        />
      </Grid>
      <Grid item>
        <RangePickerFormContainer
          initialStartDateValue={requestParams.startDate}
          initialEndDateValue={requestParams.endDate}
          onApply={applyFilter}
          definedRanges={[
            getCustomRange({
              messageId: DATE_RANGE_FILTERS.ALL,
              startDate: firstSeenStartOfDay || millisecondsToSeconds(+new Date()),
              endDate: lastSeenEndOfDay || millisecondsToSeconds(+new Date()),
              dataTestId: "btn_all"
            }),
            ...getBasicRangesSet()
          ]}
          rangeType={DATE_RANGE_TYPE.RESOURCES}
          minDate={firstSeenStartOfDay}
          maxDate={lastSeenEndOfDay}
        />
      </Grid>
      <Grid item xs={12}>
        {[RESOURCE_PAGE_EXPENSES_TABS.GROUPED, RESOURCE_PAGE_EXPENSES_TABS.DETAILED].includes(activeExpensesMode) && (
          <ResourceRawExpensesContainer
            resourceId={resourceId}
            startDate={requestParams.startDate}
            endDate={requestParams.endDate}
            expensesMode={activeExpensesMode}
          />
        )}
        {[RESOURCE_PAGE_EXPENSES_TABS.PAID_NETWORK_TRAFFIC].includes(activeExpensesMode) && (
          <ResourcePaidNetworkTrafficContainer
            resourceId={resourceId}
            startDate={requestParams.startDate}
            endDate={requestParams.endDate}
          />
        )}
      </Grid>
    </Grid>
  );
};

export default ResourceExpenses;
