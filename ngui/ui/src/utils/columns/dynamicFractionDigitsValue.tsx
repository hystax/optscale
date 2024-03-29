import { FormattedMessage } from "react-intl";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import TextWithDataTestId from "components/TextWithDataTestId";

const dynamicFractionDigitsValue = ({ headerDataTestId, titleMessageId, accessorKey } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={titleMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <DynamicFractionDigitsValue value={cell.getValue()} />
});

export default dynamicFractionDigitsValue;
