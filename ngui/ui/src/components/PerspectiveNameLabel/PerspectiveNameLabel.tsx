import { Box } from "@mui/material";
import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis } from "utils/strings";
import { PerspectiveNameLabelProps } from "./types";

const MAX_NAME_LENGTH = 50;

const PerspectiveNameLabel = ({ name }: PerspectiveNameLabelProps) => {
  const isNameLong = name.length > MAX_NAME_LENGTH;

  return (
    <Tooltip title={isNameLong ? name : undefined}>
      <Box
        component="span"
        sx={{
          whiteSpaceCollapse: "preserve",
        }}
      >
        {isNameLong ? sliceByLimitWithEllipsis(name, MAX_NAME_LENGTH) : name}
      </Box>
    </Tooltip>
  );
};

export default PerspectiveNameLabel;
