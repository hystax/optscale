import Typography from "@mui/material/Typography";

const WidgetTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h3" variant="subtitle1" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

export default WidgetTitle;
