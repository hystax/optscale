import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const name = ({ captionAccessor, headerDataTestId, accessorKey = "name", enableTextCopy = false }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ row: { original }, cell }) => (
    <CaptionedCell caption={original[captionAccessor]} enableTextCopy={enableTextCopy}>
      <strong>{cell.getValue()}</strong>
    </CaptionedCell>
  )
});

export default name;
