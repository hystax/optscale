import { useMemo } from "react";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { getColumns } from "./utils";

const MlExecutorsTable = ({
  executors,
  withExpenses = false,
  disableExecutorLink = false,
  disableLocationLink = false,
  isLoading = false,
}) => {
  const memoizedExecutors = useMemo(() => executors, [executors]);

  const columns = useMemo(
    () =>
      getColumns({
        withExpenses,
        disableExecutorLink,
        disableLocationLink,
      }),
    [disableExecutorLink, disableLocationLink, withExpenses]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table data={memoizedExecutors} columns={columns} localization={{ emptyMessageId: "noExecutors" }} pageSize={50} />
  );
};

export default MlExecutorsTable;
