import React from "react";
import MuiTabs from "@mui/material/Tabs";
import PropTypes from "prop-types";
import useStyles from "./Tabs.styles";

const Tabs = ({ children, variant = "scrollable", indicatorColor = "secondary", textColor = "primary", ...rest }) => {
  const { classes } = useStyles();

  const isScrollable = variant === "scrollable";

  return (
    <MuiTabs
      variant={variant}
      textColor={textColor}
      indicatorColor={indicatorColor}
      scrollButtons={isScrollable ?? "auto"}
      allowScrollButtonsMobile
      TabScrollButtonProps={{
        classes: {
          disabled: isScrollable ? classes.hiddenTabScrollButton : ""
        }
      }}
      {...rest}
    >
      {children}
    </MuiTabs>
  );
};

Tabs.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.string,
  indicatorColor: PropTypes.string,
  textColor: PropTypes.string
};

export default Tabs;
