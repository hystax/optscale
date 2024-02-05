import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const conditions = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_conditions">
      <FormattedMessage id="conditions" />
    </TextWithDataTestId>
  ),
  accessorKey: "conditionsObject.conditionsString",
  cell: ({ row: { original } }) => original.conditionsObject.conditionsRender
});

export default conditions;
