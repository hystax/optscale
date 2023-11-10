import TextWithDataTestId from "components/TextWithDataTestId";
import { RowActions } from "../components";

const poolActions = () => ({
  header: <TextWithDataTestId dataTestId="lbl_actions" messageId="actions" />,
  id: "actions",
  enableSorting: false,
  cell: RowActions,
  enableHiding: false
});

export default poolActions;
