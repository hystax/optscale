import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LabelChip from "components/LabelChip";
import TextWithDataTestId from "components/TextWithDataTestId";
import { SPACING_1 } from "utils/layouts";

const datasetLabels = ({ id, accessorFn, accessorKey, style }) => ({
  id,
  accessorFn,
  accessorKey,
  enableSorting: false,
  style,
  header: (
    <TextWithDataTestId dataTestId="lbl_labels">
      <FormattedMessage id="labels" />
    </TextWithDataTestId>
  ),
  cell: ({ cell }) => (
    <Box display="flex" gap={SPACING_1} flexWrap="wrap">
      {cell.getValue().map((label) => (
        <LabelChip key={label} label={label} />
      ))}
    </Box>
  )
});

export default datasetLabels;
