import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

export const cpu = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_cpu">
      <FormattedMessage id="cpu" />
    </TextWithDataTestId>
  ),
  defaultSort: "asc",
  accessorKey: "cpu"
});
