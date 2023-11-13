import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlDataLocation = ({ headerDataTestId = "lbl_data_location", accessorKey = "data_location" } = {}) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="dataLocation" />
    </TextWithDataTestId>
  ),
  accessorKey
});

export default mlDataLocation;
