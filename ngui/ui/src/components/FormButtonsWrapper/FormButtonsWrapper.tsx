import React from "react";
import Box from "@mui/material/Box";
import useStyles from "./FormButtonsWrapper.styles";

type FormButtonsWrapperProps = {
  children: React.ReactNode;
  alignItems?: React.CSSProperties["alignItems"];
  justifyContent?: React.CSSProperties["justifyContent"];
  mt?: number;
  mb?: number;
};

const FormButtonsWrapper = ({
  children,
  justifyContent = "flex-start",
  alignItems,
  mt = 2,
  mb = 0
}: FormButtonsWrapperProps) => {
  const { classes } = useStyles();
  return (
    <Box display="flex" mt={mt} mb={mb} justifyContent={justifyContent} alignItems={alignItems} className={classes.wrapper}>
      {children}
    </Box>
  );
};

export default FormButtonsWrapper;
