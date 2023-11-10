import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const size = ({ headerDataTestId, accessorKey = "flavor" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="size" />
    </TextWithDataTestId>
  ),
  accessorKey
});

export default size;
