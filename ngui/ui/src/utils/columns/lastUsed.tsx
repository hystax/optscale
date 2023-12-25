import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { intl } from "translations/react-intl-config";
import { unixTimestampToDateTime } from "utils/datetime";

const lastUsed = ({
  id = "last_used",
  headerDataTestId = "last_used_label",
  titleMessageId = "lastUsed",
  accessorKey = "last_used",
  accessorFn,
  defaultSort
} = {}) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={titleMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  accessorFn,
  defaultSort,
  cell: ({ cell }) => {
    const value = cell.getValue();

    return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
  },
  globalFilterFn: (cellValue, filterValue) => {
    const search = filterValue.toLocaleLowerCase();
    const formattedCellValue = cellValue === 0 ? intl.formatMessage({ id: "never" }) : unixTimestampToDateTime(cellValue);

    return formattedCellValue.toLocaleLowerCase().includes(search);
  }
});

export default lastUsed;
