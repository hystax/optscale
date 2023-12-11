import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { formatTimeString, parse } from "utils/datetime";

const formattedTime = ({
  id,
  accessorKey,
  accessorFn,
  headerMessageId,
  headerDataTestId,
  timeStringFormat,
  parsedTimeStringFormat
}) => ({
  id,
  accessorKey,
  accessorFn,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  sortingFn: (rowA, rowB) => {
    const valueA = rowA.getValue(accessorKey || id);
    const valueB = rowB.getValue(accessorKey || id);

    const aDate = parse(valueA, timeStringFormat, new Date());
    const bDate = parse(valueB, timeStringFormat, new Date());

    return aDate - bDate;
  },
  cell: ({ cell }) =>
    formatTimeString({
      timeString: cell.getValue(),
      timeStringFormat,
      parsedTimeStringFormat
    }),
  globalFilterFn: (cellValue, filterValue) => {
    const search = filterValue.toLocaleLowerCase();
    const formattedCellValue = formatTimeString({
      timeString: cellValue,
      timeStringFormat,
      parsedTimeStringFormat
    });

    return formattedCellValue.toLocaleLowerCase().includes(search);
  }
});

export default formattedTime;
