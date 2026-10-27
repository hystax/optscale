import { ReactNode } from "react";
import { Box, FormControl, FormHelperText } from "@mui/material";

type FieldWithActionButtonProps = {
  children: ReactNode;
  button?: ReactNode;
  errorMessage?: ReactNode;
};

const FieldWithActionButton = ({ children, button, errorMessage }: FieldWithActionButtonProps) => (
  <FormControl fullWidth>
    <Box sx={{ display: "flex", flexDirection: "row", gap: 1, alignItems: "center" }}>
      <Box sx={{ flexGrow: 1 }}>{children}</Box>
      {button && <Box>{button}</Box>}
    </Box>
    {errorMessage && <FormHelperText error>{errorMessage}</FormHelperText>}
  </FormControl>
);

export default FieldWithActionButton;
