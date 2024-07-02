import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import SlicedText from "components/SlicedText";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const DEFAULT_MAX_TEXT_LENGTH = 50;

const slicedText = ({
  headerMessageId,
  headerDataTestId,
  id,
  accessorFn,
  accessorKey,
  maxTextLength = DEFAULT_MAX_TEXT_LENGTH,
  copy = false,
  enableSorting
} = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorKey,
  accessorFn,
  enableSorting,
  cell: ({ cell }) => {
    const text = cell.getValue();

    if (!text) {
      return CELL_EMPTY_VALUE;
    }

    const slicedTextElement = <SlicedText limit={maxTextLength} text={text} />;

    if (copy) {
      return <CopyText text={text}>{slicedTextElement}</CopyText>;
    }

    return slicedTextElement;
  }
});

export default slicedText;
