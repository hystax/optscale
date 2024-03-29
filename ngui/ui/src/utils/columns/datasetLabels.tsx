import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LabelChip from "components/LabelChip";
import TextWithDataTestId from "components/TextWithDataTestId";
import { SPACING_1 } from "utils/layouts";

const datasetLabels = ({ id, accessorFn, style }) => ({
  id,
  accessorFn: (original) => accessorFn(original).join(" "),
  enableSorting: false,
  style,
  header: (
    <TextWithDataTestId dataTestId="lbl_labels">
      <FormattedMessage id="labels" />
    </TextWithDataTestId>
  ),
  cell: ({ row: { original } }) => {
    const cellValue = accessorFn(original);

    return (
      <Box display="flex" gap={SPACING_1} flexWrap="wrap">
        {cellValue.map((label) => (
          <LabelChip key={label} label={label} />
        ))}
      </Box>
    );
  }
});

export default datasetLabels;
