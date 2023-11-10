import Typography from "@mui/material/Typography";

const SubTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h4" variant="subtitle1" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

export default SubTitle;
