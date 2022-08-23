import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, secondsToMilliseconds, format } from "utils/datetime";

const violatedAt = () => ({
  Header: (
    <TextWithDataTestId dataTestId="lbl_violated_at">
      <FormattedMessage id="violatedAt" />
    </TextWithDataTestId>
  ),
  accessor: "created_at",
  Cell: ({ cell: { value } }) => format(secondsToMilliseconds(value), EN_FULL_FORMAT),
  defaultSort: "desc"
});

export default violatedAt;
