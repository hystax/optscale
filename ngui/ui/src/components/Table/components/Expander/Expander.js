import React from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import IconButton from "@mui/material/IconButton";
import PropTypes from "prop-types";
import { v4 as uuidv4 } from "uuid";
import useStyles from "./Expander.styles";

const Expander = ({ row }) => {
  const { depth } = row;

  const isExpanded = row.getIsExpanded();

  const { classes, cx } = useStyles();

  const expandPadding = Array(depth)
    .fill()
    .map(() => <span className={classes.treePadding} key={uuidv4()} />);

  const expandIcon = (
    <IconButton
      className={cx(classes.expand, {
        [classes.expandOpen]: isExpanded, // todo: figure out how we can save previous state of expander to apply animations (each expander click changes rows completely)
        [classes.visibilityHidden]: !row.getCanExpand()
      })}
      onClick={(e) => {
        row.getToggleExpandedHandler()();
        e.stopPropagation();
      }}
    >
      <ExpandMoreIcon />
    </IconButton>
  );

  return (
    <>
      {expandPadding}
      {expandIcon}
    </>
  );
};

Expander.propTypes = {
  row: PropTypes.object.isRequired
};

export default Expander;
