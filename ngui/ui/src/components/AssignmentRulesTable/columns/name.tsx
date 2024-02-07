import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import SlicedText from "components/SlicedText";
import TextWithDataTestId from "components/TextWithDataTestId";

const name = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_name">
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey: "name",
  cell: ({ row: { original } }) => (
    <CircleLabel
      figureColor={original.active ? "success" : "info"}
      label={<SlicedText limit={32} text={original.name} />}
      tooltip={{ show: true, messageId: original.active ? "active" : "inactive", placement: "right" }}
    />
  )
});

export default name;
