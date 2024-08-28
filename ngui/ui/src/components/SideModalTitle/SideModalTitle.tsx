import Typography, { TypographyProps } from "@mui/material/Typography";

type SideModalTitleProps = {
  dataProductTourId?: string;
  dataTestId?: string;
} & TypographyProps;

const SideModalTitle = ({ children, dataProductTourId, dataTestId, ...rest }: SideModalTitleProps) => (
  <Typography component="h2" variant="h6" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

export default SideModalTitle;
