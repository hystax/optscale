import React from "react";
import Typography, { type TypographyProps } from "@mui/material/Typography";

type SubTitleProps = {
  children: React.ReactNode;
  dataProductTourId?: string;
  dataTestId?: string;
} & TypographyProps;

const SubTitle = ({ children, dataProductTourId, dataTestId, ...rest }: SubTitleProps) => (
  <Typography component="h4" variant="subtitle1" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

export default SubTitle;
