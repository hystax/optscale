import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FORMAT, unixTimestampToDateTime } from "utils/datetime";

const utcTime = ({ id, accessorFn, headerMessageId, headerDataTestId, format = EN_FORMAT, defaultSort }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  id,
  accessorFn: (originalRow) => {
    const value = accessorFn(originalRow);

    return value ? unixTimestampToDateTime(value, format) : undefined;
  },
  defaultSort
});

export default utcTime;
