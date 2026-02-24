import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const name = ({ captionAccessor, headerDataTestId, accessorKey = "name", enableTextCopy = false, defaultSort }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey,
  defaultSort,
  cell: ({ row: { original }, cell }) => (
    <CaptionedCell caption={original[captionAccessor]} enableTextCopy={enableTextCopy}>
      <strong>{cell.getValue()}</strong>
    </CaptionedCell>
  ),
});

export default name;
