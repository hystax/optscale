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
  setSelectedPools,
  isChangeSettingsAllowed,
  isLoading = false,
  onSelectionChange
}) => {
  const tableData = useMemo(() => {
    const excludedPoolsIds = Object.keys(currentExcludedPools);
    return isChangeSettingsAllowed ? availablePools : availablePools.filter(({ id }) => excludedPoolsIds.includes(id));
  }, [availablePools, currentExcludedPools, isChangeSettingsAllowed]);

  const columns = useMemo(
    () => [
      {
        Header: <FormattedMessage id="name" />,
        accessor: "name",
        Cell: ({ row: { original } }) => (
          <PoolLabel id={original.id} name={original.name} type={original.pool_purpose} disableLink />
        ),
        defaultSort: "asc"
      }
    ],
    []
  );

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
      addSelectionColumn={isChangeSettingsAllowed}
      setSelectedRows={isChangeSettingsAllowed ? setSelectedPools : undefined}
      withSearch
      initialSelectedRows={currentExcludedPools}
      getRowId={getRowId}
      onSelectionChange={onSelectionChange}
    />
  );
};

ExcludedPoolsTable.propTypes = {
  availablePools: PropTypes.array.isRequired,
  setSelectedPools: PropTypes.func.isRequired,
  currentExcludedPools: PropTypes.object.isRequired,
  onSelectionChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isChangeSettingsAllowed: PropTypes.bool
};

export default ExcludedPoolsTable;
