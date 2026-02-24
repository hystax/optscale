import { lastUsed, firstSeen, mlExecutorLocation, expenses } from "utils/columns";
import executor from "utils/columns/executor";

export const getColumns = ({ withExpenses = false, disableExecutorLink = false, disableLocationLink = false } = {}) => [
  executor({
    disableLink: disableExecutorLink,
  }),
  mlExecutorLocation({
    disableLink: disableLocationLink,
  }),
  ...(withExpenses
    ? [
        expenses({
          id: "expenses",
          headerDataTestId: "lbl_expenses",
          headerMessageId: "expenses",
          accessorFn: (rowData) => rowData.resource?.total_cost,
        }),
      ]
    : []),
  lastUsed({ headerDataTestId: "lbl_last_used", accessorFn: (rowData) => rowData.last_used }),
  firstSeen({ headerDataTestId: "lbl_first_seen", accessorFn: (rowData) => rowData.resource?.first_seen }),
];
