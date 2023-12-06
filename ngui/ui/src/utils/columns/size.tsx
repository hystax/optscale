import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const size = ({ headerDataTestId, id, accessorKey = "flavor", accessorFn }) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="size" />
    </TextWithDataTestId>
  ),
  accessorFn,
  accessorKey
});

export default size;
