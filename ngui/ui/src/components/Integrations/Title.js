import React from "react";
import { Box } from "@mui/material";

const Title = ({ icon, label }) => (
  <Box
    sx={{
      display: "flex",
      alignItems: "center",
      columnGap: (theme) => theme.spacing(1)
    }}
  >
    {icon}
    <Box>{label}</Box>
  </Box>
);

export default Title;
