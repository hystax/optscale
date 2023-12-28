import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import PoolLabel from "components/PoolLabel";
import Table from "components/Table";
import TableLoader from "components/TableLoader";

type SelectedPoolType = { [key: string]: [value: boolean] };

type ExcludedPoolsTableType = {
  availablePools: {
    id: string;
  }[];
  isLoading: boolean;
  isChangeSettingsAllowed: boolean;
  selectedPools: SelectedPoolType;
  onSelectedPoolChange: (pools: SelectedPoolType) => void;
};

const ExcludedPoolsTable = ({
  availablePools,
  isChangeSettingsAllowed,
  isLoading = false,
  selectedPools,
  onSelectedPoolChange
}: ExcludedPoolsTableType) => {
  const tableData = useMemo(() => {
    const excludedPoolsIds = Object.keys(selectedPools);
    return isChangeSettingsAllowed ? availablePools : availablePools.filter(({ id }) => excludedPoolsIds.includes(id));
  }, [availablePools, selectedPools, isChangeSettingsAllowed]);

  const columns = useMemo(
    () => [
      {
        header: <FormattedMessage id="name" />,
        accessorKey: "name",
        cell: ({ row: { original } }) => (
          <PoolLabel id={original.id} name={original.name} type={original.pool_purpose} disableLink />
        ),
        defaultSort: "asc"
      }
    ],
    []
  );

  const getRowSelectionProps = () => ({
    withSelection: true,
    rowSelection: selectedPools,
    onRowSelectionChange: (pools: SelectedPoolType) => onSelectedPoolChange(pools)
  });

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} />
  ) : (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noExclusions"
      }}
      counters={{ showCounters: true, hideDisplayed: true }}
      withSearch
      queryParamPrefix="excludePools"
      getRowId={(row) => row.id}
      enableSearchQueryParam={false}
      {...(isChangeSettingsAllowed ? getRowSelectionProps() : {})}
    />
  );
};

export default ExcludedPoolsTable;
