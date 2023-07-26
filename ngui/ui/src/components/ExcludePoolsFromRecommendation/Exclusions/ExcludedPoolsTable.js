import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import PoolLabel from "components/PoolLabel";
import Table from "components/Table";
import TableLoader from "components/TableLoader";

const getRowId = (row) => row.id;

const ExcludedPoolsTable = ({
  availablePools,
  currentExcludedPools,
  isChangeSettingsAllowed,
  isLoading = false,
  selectedPoolIds,
  onSelectedPoolIdsChange
}) => {
  const tableData = useMemo(() => {
    const excludedPoolsIds = Object.keys(currentExcludedPools);
    return isChangeSettingsAllowed ? availablePools : availablePools.filter(({ id }) => excludedPoolsIds.includes(id));
  }, [availablePools, currentExcludedPools, isChangeSettingsAllowed]);

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

  const getRowSelectionProps = () => {
    const rowSelectionState = Object.fromEntries(selectedPoolIds.map((id) => [id, true]));

    return {
      withSelection: true,
      rowSelection: rowSelectionState,
      onRowSelectionChange: (newState) => {
        onSelectedPoolIdsChange(Object.keys(newState));
      }
    };
  };

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
      initialSelectedRows={currentExcludedPools}
      getRowId={getRowId}
      {...(isChangeSettingsAllowed ? getRowSelectionProps() : {})}
    />
  );
};

ExcludedPoolsTable.propTypes = {
  availablePools: PropTypes.array.isRequired,
  currentExcludedPools: PropTypes.object.isRequired,
  onSelectedPoolIdsChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isChangeSettingsAllowed: PropTypes.bool,
  selectedPoolIds: PropTypes.array
};

export default ExcludedPoolsTable;
