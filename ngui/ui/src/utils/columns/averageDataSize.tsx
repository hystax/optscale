import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import TextWithDataTestId from "components/TextWithDataTestId";

const averageDataSize = ({ headerDataTestId, accessorKey }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="dataSizeAvg" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <FormattedDigitalUnit value={cell.getValue()} baseUnit={SI_UNITS.MEGABYTE} maximumFractionDigits={2} />
});

export default averageDataSize;
