import React from "react";
import HorizontalRuleIcon from "@mui/icons-material/HorizontalRule";
import { Breadcrumbs as MuiBreadcrumbs } from "@mui/material";
import PropTypes from "prop-types";
import useStyles from "./Breadcrumbs.styles";

const Breadcrumbs = ({ children, withSlashAtTheEnd = false }) => {
  const { classes } = useStyles();

  return (
    <MuiBreadcrumbs
      classes={{
        separator: classes.separator
      }}
      separator={
        <HorizontalRuleIcon
          sx={{
            transform: "rotate(115deg)"
          }}
          color="info"
          fontSize="small"
        />
      }
    >
      {children}
      {withSlashAtTheEnd && <span />}
    </MuiBreadcrumbs>
  );
};

Breadcrumbs.propTypes = {
  children: PropTypes.node,
  withSlashAtTheEnd: PropTypes.bool
};

export default Breadcrumbs;
