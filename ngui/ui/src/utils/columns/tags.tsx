import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const tags = ({
  headerDataTestId = "lbl_tags",
  id,
  accessorKey,
  accessorFn,
  columnSelector,
  enableSorting = false,
  getTags
}) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="tags" />
    </TextWithDataTestId>
  ),
  columnSelector,
  accessorKey,
  accessorFn,
  enableSorting,
  style: {
    minWidth: "200px"
  },
  cell: ({ row: { original } }) => <CollapsableTableCell maxRows={5} tags={getTags(original)} />
});

export default tags;
