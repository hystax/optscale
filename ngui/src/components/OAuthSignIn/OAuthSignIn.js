import React from "react";
import Grid from "@mui/material/Grid";
import { FormattedMessage } from "react-intl";
import GoogleAuthButton from "components/GoogleAuthButton";
import MicrosoftSignInButton from "components/MicrosoftSignInButton";
import SubTitle from "components/SubTitle";
import { SPACING_1 } from "utils/layouts";

const OAuthSignIn = () => (
  <Grid container alignItems="center" justifyContent="center" spacing={SPACING_1}>
    <Grid item xs={12}>
      <SubTitle>
        <FormattedMessage id="signInWith" />
      </SubTitle>
    </Grid>
    <Grid item xs={6}>
      <GoogleAuthButton />
    </Grid>
    <Grid item xs={6}>
      <MicrosoftSignInButton />
    </Grid>
  </Grid>
);

export default OAuthSignIn;
