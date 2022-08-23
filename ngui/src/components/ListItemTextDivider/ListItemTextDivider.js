import React from "react";
import ListItem from "@mui/material/ListItem";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import useStyles from "./ListItemTextDivider.styles";

const ListItemTextDivider = ({ messageId, color = "inherit" }) => {
  const { classes } = useStyles();
  return (
    <ListItem className={classes.textWrapper}>
      <Typography color={color} variant="caption" className={classes.text}>
        <FormattedMessage id={messageId} />
      </Typography>
    </ListItem>
  );
};

ListItemTextDivider.propTypes = {
  messageId: PropTypes.string.isRequired,
  color: PropTypes.string
};

export default ListItemTextDivider;
