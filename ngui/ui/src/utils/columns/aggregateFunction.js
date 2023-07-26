import React from "react";
import AggregateFunctionFormattedMessage from "components/AggregateFunctionFormattedMessage";
import HeaderHelperCell from "components/HeaderHelperCell";

const aggregateFunction = ({ headerDataTestId = "lbl_aggregate", accessorKey = "func" } = {}) => ({
  header: (
    <HeaderHelperCell
      titleDataTestId={headerDataTestId}
      titleMessageId="aggregateFunction"
      helperMessageId="aggregateFunctionTooltip"
    />
  ),
  accessorKey,
  cell: ({ cell }) => <AggregateFunctionFormattedMessage aggregateFunction={cell.getValue()} />
});

export default aggregateFunction;
