import React from "react";
import TendencyFormattedMessage from "components/TendencyFormattedMessage";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const tendency = ({ headerDataTestId = "lbl_tendency", accessorKey = "tendency" } = {}) => ({
  header: <TextWithDataTestId dataTestId={headerDataTestId} messageId="tendency" />,
  accessorKey,
  cell: ({ cell }) => {
    const tendencyValue = cell.getValue();

    return tendencyValue ? <TendencyFormattedMessage tendency={tendencyValue} /> : CELL_EMPTY_VALUE;
  }
});

export default tendency;
