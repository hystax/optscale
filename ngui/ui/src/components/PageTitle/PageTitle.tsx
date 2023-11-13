import { forwardRef } from "react";
import Typography from "@mui/material/Typography";

const PageTitle = forwardRef(({ children, dataProductTourId, dataTestId, ...rest }, ref) => (
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
));

export default PageTitle;
