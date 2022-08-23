import React, { useMemo } from "react";
import Table from "components/Table";

/* This component wraps columns and data with useMemo for storybook */
const TableUseMemoWrapper = ({ data, columns, ...other }) => {
  const memoizedData = useMemo(() => data, [data]);
  const memoizedColumns = useMemo(() => columns, [columns]);

  return <Table data={memoizedData} columns={memoizedColumns} {...other} />;
};

export default TableUseMemoWrapper;
