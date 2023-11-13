import Typography from "@mui/material/Typography";
import { SPACING_1 } from "utils/layouts";

// TODO - check why table does not inherit variant size everywhere, on;y on OrganizationOverview
const TabContent = ({ children, variant, value, index, id, ariaLabelledby, ...rest }) => (
  <Typography
    component="div"
    role="tabpanel"
    hidden={value !== index}
    id={id}
    aria-labelledby={ariaLabelledby}
    variant={variant}
    {...rest}
    style={{ paddingTop: `${SPACING_1}rem` }}
  >
    {children}
  </Typography>
);

export default TabContent;
