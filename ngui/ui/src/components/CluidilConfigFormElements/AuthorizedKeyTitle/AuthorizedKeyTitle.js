import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";

const AuthorizedKeyTitle = () => (
  <Typography fontWeight="bold" gutterBottom>
    <FormattedMessage id="authorizedKey" />
  </Typography>
);

export default AuthorizedKeyTitle;
