import { FormattedMessage } from "react-intl";
import TextBlock from "components/TextBlock";
import TextWithDataTestId from "components/TextWithDataTestId";

const status = ({ headerDataTestId, accessorKey }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="status" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => {
    const statusValue = cell.getValue();

    return (
      <TextBlock
        color={statusValue}
        messageId={{ success: "allGood", ok: "ok", warning: "requiresAttention", error: "critical" }[statusValue] || "unknown"}
      />
    );
  }
});

export default status;
