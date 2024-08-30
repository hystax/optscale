import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, format as formatFn } from "utils/datetime";

const localTime = ({
  id,
  accessorFn,
  headerMessageId,
  headerDataTestId,
  format = EN_FULL_FORMAT,
  defaultSort,
  enableSorting
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorFn: (originalRow) => {
    const value = accessorFn(originalRow);

    return value ? formatFn(value, format) : undefined;
  },
  defaultSort,
  enableSorting
});

export default localTime;
