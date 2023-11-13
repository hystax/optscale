import { FormattedMessage } from "react-intl";
import BINextExportTimeLabel from "components/BINextExportTimeLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getBIExportActivityStatus } from "utils/biExport";

const biExportNextExport = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_next_export">
      <FormattedMessage id="nextExport" />
    </TextWithDataTestId>
  ),
  accessorKey: "next_run",
  enableSorting: false,
  cell: ({ cell, row: { original } }) => {
    const nextRun = cell.getValue();

    const activity = getBIExportActivityStatus(original.status);

    return <BINextExportTimeLabel nextRun={nextRun} activity={activity} />;
  }
});

export default biExportNextExport;
