import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const priority = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_priority">
      <FormattedMessage id="priority" />
    </TextWithDataTestId>
  ),
  accessorKey: "priority",
  defaultSort: "asc"
});

export default priority;
