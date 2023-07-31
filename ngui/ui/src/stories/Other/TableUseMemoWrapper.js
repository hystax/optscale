import React, { useMemo } from "react";
import Table from "components/Table";

/* This component wraps columns and data with useMemo for storybook */
const TableUseMemoWrapper = ({ data, columns, ...rest }) => {
  const memoizedData = useMemo(() => data, [data]);
  const memoizedColumns = useMemo(() => columns, [columns]);

  return <Table data={memoizedData} columns={memoizedColumns} {...rest} />;
};

export default TableUseMemoWrapper;
