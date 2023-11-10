import Grid from "@mui/material/Grid";
import { FormattedMessage } from "react-intl";
import SubTitle from "components/SubTitle";
import { SPACING_1 } from "utils/layouts";

const OAuthSignIn = ({ googleButton, microsoftButton }) => (
  <Grid container alignItems="center" justifyContent="center" spacing={SPACING_1}>
    <Grid item xs={12}>
      <SubTitle>
        <FormattedMessage id="signInWith" />
      </SubTitle>
    </Grid>
    <Grid item xs={6}>
      {googleButton}
    </Grid>
    <Grid item xs={6}>
      {microsoftButton}
    </Grid>
  </Grid>
);

export default OAuthSignIn;
