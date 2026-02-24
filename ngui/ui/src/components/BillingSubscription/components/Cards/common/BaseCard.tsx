import { ReactNode } from "react";
import { Box, Paper, Stack } from "@mui/material";
import { SPACING_2 } from "utils/layouts";

type BaseCardProps = {
  body: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
};

export const sizeSpec = {
  maxWidth: 560,
  minWidth: 240,
  minHeight: 220,
};

const BaseCard = ({ header, body, footer }: BaseCardProps) => (
  <Paper
    variant="outlined"
    elevation={0}
    sx={{
      width: "100%",
      display: "flex",
      ...sizeSpec,
      padding: SPACING_2,
    }}
  >
    <Stack spacing={SPACING_2} flexGrow={1}>
      {!!header && (
        <Box minHeight={32} display="flex" alignItems="center">
          {header}
        </Box>
      )}
      <Box flexGrow={1}>{body}</Box>
      {!!footer && <Box>{footer}</Box>}
    </Stack>
  </Paper>
);

export default BaseCard;
