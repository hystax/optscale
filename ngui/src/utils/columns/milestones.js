import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const milestones = ({
  headerMessageId = "milestones",
  headerDataTestId = "lbl_milestones",
  accessor = "milestoneNames",
  disableSortBy = true
} = {}) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessor,
  disableSortBy,
  Cell: ({ cell: { value } }) => value.map((name) => <div key={name}>{name}</div>)
});

export default milestones;
