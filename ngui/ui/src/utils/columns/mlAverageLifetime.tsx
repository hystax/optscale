import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatDuration } from "hooks/useFormatDuration";
import { secondsToMilliseconds } from "utils/datetime";

const LifeTime = (value) => useFormatDuration(secondsToMilliseconds(value), 1);

const mlAverageLifetime = ({ headerDataTestId = "lbl_average_lifetime", accessorKey = "average_lifetime" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="averageLifetime" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <LifeTime value={cell.getValue()} />
});

export default mlAverageLifetime;
