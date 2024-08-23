import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LabelChip from "components/LabelChip";
import TextWithDataTestId from "components/TextWithDataTestId";
import { SPACING_1 } from "utils/layouts";

const leaderboardDatasetLabels = () => ({
  id: "labels",
  accessorFn: (originalRow) => originalRow.labels.join(" "),
  enableSorting: false,
  header: (
    <TextWithDataTestId dataTestId="lbl_labels">
      <FormattedMessage id="labels" />
    </TextWithDataTestId>
  ),
  cell: ({
    row: {
      original: { labels }
    }
  }) => (
    <Box display="flex" gap={SPACING_1} flexWrap="wrap">
      {labels.map((label) => (
        <LabelChip key={label} label={label} />
      ))}
    </Box>
  )
});

export default leaderboardDatasetLabels;
