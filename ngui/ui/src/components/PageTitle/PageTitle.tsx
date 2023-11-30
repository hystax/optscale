import { forwardRef } from "react";
import Typography, { type TypographyProps } from "@mui/material/Typography";

type PageTitleCustomProps = {
  dataTestId: string;
  dataProductTourId?: string;
};

type PageTitleProps = TypographyProps<"h1"> & PageTitleCustomProps;

const PageTitle = forwardRef<HTMLHeadingElement, PageTitleProps>(
  ({ children, dataProductTourId, dataTestId, ...rest }, ref) => (
    <Typography
      component="h1"
      variant="h6"
      data-product-tour-id={dataProductTourId}
      data-test-id={dataTestId}
      ref={ref}
      {...rest}
    >
      {children}
    </Typography>
  )
);

export default PageTitle;
