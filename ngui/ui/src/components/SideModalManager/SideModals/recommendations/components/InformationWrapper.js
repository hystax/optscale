import React from "react";
import { Box } from "@mui/material";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_1 } from "utils/layouts";

const InformationWrapper = ({ children }) => (
  <>
    <Box mb={SPACING_1}>
      <InlineSeverityAlert messageId="recommendationsSettingsOutOfSyncMessage" />
    </Box>
    {children}
  </>
);

export default InformationWrapper;
