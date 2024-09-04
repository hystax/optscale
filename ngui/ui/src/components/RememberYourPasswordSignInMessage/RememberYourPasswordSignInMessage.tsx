import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { LOGIN } from "urls";

const RememberYourPasswordSignInMessage = () => (
  <Typography>
    <Link color="primary" to={LOGIN} component={RouterLink}>
      <FormattedMessage id="rememberYourPasswordSignIn" />
    </Link>
  </Typography>
);

export default RememberYourPasswordSignInMessage;
