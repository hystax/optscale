import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, secondsToMilliseconds, format } from "utils/datetime";

const violatedAt = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_violated_at">
      <FormattedMessage id="violatedAt" />
    </TextWithDataTestId>
  ),
  accessorKey: "created_at",
  cell: ({ cell }) => format(secondsToMilliseconds(cell.getValue()), EN_FULL_FORMAT),
  defaultSort: "desc"
});

export default violatedAt;
