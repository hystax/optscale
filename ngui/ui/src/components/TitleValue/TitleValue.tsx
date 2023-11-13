import { forwardRef } from "react";
import Typography from "@mui/material/Typography";

const TitleValue = forwardRef(({ children, dataTestId, style = {}, ...rest }, ref) => (
  <Typography
    component="span"
    variant="subtitle1"
    data-test-id={dataTestId}
    style={{ ...style, fontWeight: "bold" }}
    ref={ref}
    {...rest}
  >
    {children}
  </Typography>
));

export default TitleValue;
