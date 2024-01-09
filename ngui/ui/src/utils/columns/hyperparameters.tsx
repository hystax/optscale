import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const hyperparameters = ({ accessorKey = "hyperparameters" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_hyperparameters">
      <FormattedMessage id="hyperparameters" />
    </TextWithDataTestId>
  ),
  accessorKey,
  enableSorting: false,
  cell: ({ cell }) => {
    if (isEmpty(hyperparameters)) {
      return CELL_EMPTY_VALUE;
    }
    return <CollapsableTableCell maxRows={5} tags={cell.getValue()} />;
  }
});

export default hyperparameters;
