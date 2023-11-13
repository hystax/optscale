import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getTimeDistance } from "utils/datetime";

const biExportLastSuccessfulExport = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_last_successful_export">
      <FormattedMessage id="lastSuccessfulExport" />
    </TextWithDataTestId>
  ),
  accessorKey: "last_completed",
  cell: ({ row: { original }, cell }) =>
    original.last_completed === 0 ? (
      <FormattedMessage id="never" />
    ) : (
      <FormattedMessage
        id="valueAgo"
        values={{
          value: getTimeDistance(cell.getValue())
        }}
      />
    )
});

export default biExportLastSuccessfulExport;
