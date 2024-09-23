import { useMemo } from "react";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { useIsOptScaleModeEnabled } from "hooks/useIsOptScaleModeEnabled";
import { lastUsed, firstSeen, mlExecutorLocation, expenses } from "utils/columns";
import executor from "utils/columns/executor";
import { OPTSCALE_MODE } from "utils/constants";

const MlExecutorsTable = ({ executors, isLoading }) => {
  const memoizedExecutors = useMemo(() => executors, [executors]);

  const isFinOpsEnabled = useIsOptScaleModeEnabled(OPTSCALE_MODE.FINOPS);

  const columns = useMemo(
    () => [
      executor(),
      mlExecutorLocation(),
      ...(isFinOpsEnabled
        ? [
            expenses({
              id: "expenses",
              headerDataTestId: "lbl_expenses",
              headerMessageId: "expenses",
              accessorFn: (rowData) => rowData.resource?.total_cost
            })
          ]
        : []),
      lastUsed({ headerDataTestId: "lbl_last_used", accessorFn: (rowData) => rowData.last_used }),
      firstSeen({ headerDataTestId: "lbl_first_seen", accessorFn: (rowData) => rowData.resource?.first_seen })
    ],
    [isFinOpsEnabled]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table data={memoizedExecutors} columns={columns} localization={{ emptyMessageId: "noExecutors" }} pageSize={50} />
  );
};

export default MlExecutorsTable;
