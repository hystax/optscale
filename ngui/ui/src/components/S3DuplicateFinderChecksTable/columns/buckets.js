import React from "react";
import { FormattedMessage } from "react-intl";
import ExpandableList from "components/ExpandableList";
import TextWithDataTestId from "components/TextWithDataTestId";

const buckets = () => ({
  header: (
    <TextWithDataTestId dataTestId="buckets">
      <FormattedMessage id="bucketsScanned" />
    </TextWithDataTestId>
  ),
  accessorKey: "bucketsString",
  enableSorting: false,
  cell: ({ row: { original } }) => {
    const { buckets: bucketsList } = original.filters;

    return <ExpandableList items={bucketsList} render={({ name }) => <div key={name}>{name}</div>} maxRows={2} />;
  }
});

export default buckets;
