import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

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
  cell: ({ row: { original } }) => {
    const tagsValue = getTags(original);

    if (isEmptyObject(tagsValue)) {
      return CELL_EMPTY_VALUE;
    }

    return <CollapsableTableCell maxRows={5} tags={tagsValue} />;
  }
});

export default tags;
