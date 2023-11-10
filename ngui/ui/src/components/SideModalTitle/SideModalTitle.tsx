import Typography from "@mui/material/Typography";

const SideModalTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h2" variant="h6" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

export default SideModalTitle;
