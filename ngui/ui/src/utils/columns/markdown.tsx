import { FormattedMessage } from "react-intl";
import Markdown from "components/Markdown";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const markdown = ({ id, accessorFn, headerMessageId, headerDataTestId, enableSorting }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorFn: (originalRow) => accessorFn(originalRow) ?? "",
  enableSorting,
  cell: ({ cell }) => {
    const description = cell.getValue();

    return description ? <Markdown>{description}</Markdown> : CELL_EMPTY_VALUE;
  }
});

export default markdown;
