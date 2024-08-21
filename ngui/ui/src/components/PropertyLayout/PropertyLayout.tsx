import { Box } from "@mui/material";
import { ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";

const PropertyLayout = ({ propertyName, propertyValue, iconButtons }) => (
  <Box display="flex" gap={SPACING_1} flexWrap="wrap">
    <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
      {propertyName}
    </Box>
    <Box flexGrow={2} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.LARGE} display="flex" gap={SPACING_1} overflow="auto">
      <Box flexGrow={1} overflow="auto">
        {propertyValue}
      </Box>
      {iconButtons && (
        <Box display="flex" height="fit-content">
          {iconButtons}
        </Box>
      )}
    </Box>
  </Box>
);

export default PropertyLayout;
