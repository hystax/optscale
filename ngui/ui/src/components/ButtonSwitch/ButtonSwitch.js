import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import Button from "components/Button";
import useStyles from "./ButtonSwitch.styles";

const ButtonSwitch = ({ buttons }) => {
  const { classes } = useStyles();
  return (
    <Box className={classes.root}>
      {buttons.map((button) => {
        const { messageId, link, icon } = button;
        return <Button key={messageId} messageId={messageId} link={link} color="primary" size="large" startIcon={icon} />;
      })}
    </Box>
  );
};

ButtonSwitch.propTypes = {
  buttons: PropTypes.array.isRequired
};

export default ButtonSwitch;
