import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlComputeLocation = ({ headerDataTestId = "lbl_compute_location", accessorKey = "compute_location" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="computeLocation" />
    </TextWithDataTestId>
  ),
  accessorKey
});

export default mlComputeLocation;
