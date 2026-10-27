import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import PoolsOverview from "components/PoolsOverview";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import PoolsService, { dataMocked } from "services/PoolsService";
import { isEmptyArray } from "utils/arrays";
import { getCurrentMonthRange } from "utils/datetime";

const Pools = () => {
  const { useGet, useGetExpensesRange } = PoolsService();
  const { isLoading, data, isGetPoolAllowedActionsLoading } = useGet();
  const {
    data: expensesRangeData,
    isLoading: isExpensesRangeLoading,
    isError: isExpensesRangeError,
    startDateTimestamp,
    endDateTimestamp,
  } = useGetExpensesRange();

  const { startOfMonth: mockedStartDateTimestamp, today: mockedEndDateTimestamp } = getCurrentMonthRange(true);

  return (
    <Mocked
      mock={
        <PageMockupContextProvider>
          <PoolsOverview
            data={dataMocked}
            isLoading={false}
            isGetPoolAllowedActionsLoading={false}
            expensesRangeData={dataMocked}
            isExpensesRangeLoading={false}
            startDateTimestamp={mockedStartDateTimestamp}
            endDateTimestamp={mockedEndDateTimestamp}
          />
        </PageMockupContextProvider>
      }
      backdropMessageType={MESSAGE_TYPES.POOLS}
      mockCondition={data.limit === 0 && data.parent_id === null && isEmptyArray(data.children)}
    >
      <PoolsOverview
        data={data}
        isLoading={isLoading}
        isGetPoolAllowedActionsLoading={isGetPoolAllowedActionsLoading}
        expensesRangeData={expensesRangeData}
        isExpensesRangeLoading={isExpensesRangeLoading}
        isExpensesRangeError={isExpensesRangeError}
        startDateTimestamp={startDateTimestamp}
        endDateTimestamp={endDateTimestamp}
      />
    </Mocked>
  );
};

export default Pools;
