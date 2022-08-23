import React from "react";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import PageTitle from "components/PageTitle";
import { SPACING_2 } from "utils/layouts";
import useStyles from "./IconError.styles";

const IconError = ({ messageId, children }) => {
  const { classes } = useStyles();
  return (
    <Grid container direction="column" alignItems="center" spacing={SPACING_2}>
      <Grid item>
        <ErrorOutlineOutlinedIcon className={classes.icon} />
      </Grid>
      <Grid item>
        <PageTitle align="center">
          <FormattedMessage id={messageId} />
        </PageTitle>
      </Grid>
      <Grid item>{children}</Grid>
    </Grid>
  );
};

IconError.propTypes = {
  messageId: PropTypes.string.isRequired,
  children: PropTypes.node
};

export default IconError;
