import { FormattedMessage } from "react-intl";
import MlModelPathLabel from "components/MlModelPathLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const mlModelPath = ({ id, accessorKey, accessorFn, headerMessageId, headerDataTestId, cell }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorKey,
  accessorFn,
  cell: (cellProps) => {
    if (typeof cell === "function") {
      return cell(cellProps);
    }

    const path = cellProps.cell.getValue();

    return path ? <MlModelPathLabel path={path} /> : CELL_EMPTY_VALUE;
  }
});

export default mlModelPath;
