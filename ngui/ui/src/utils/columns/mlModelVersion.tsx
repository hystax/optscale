import { FormattedMessage } from "react-intl";
import MlModelVersionLabel from "components/MlModelVersionLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const mlModelVersion = ({ id, accessorKey, accessorFn, headerMessageId, headerDataTestId }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorKey,
  accessorFn,
  cell: ({ cell }) => {
    const version = cell.getValue();

    return version ? <MlModelVersionLabel version={version} /> : CELL_EMPTY_VALUE;
  }
});

export default mlModelVersion;
