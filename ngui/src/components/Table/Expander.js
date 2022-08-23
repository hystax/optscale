import React from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import IconButton from "@mui/material/IconButton";
import PropTypes from "prop-types";
import { v4 as uuidv4 } from "uuid";
import useStyles from "./styles/Expander.styles";

const Expander = ({ row, onExpand }) => {
  const { onClick: defaultClickHandler, ...restToggleRowExpandedProps } = row.getToggleRowExpandedProps();
  const { depth, canExpand, isExpanded, original } = row;

  const { classes, cx } = useStyles();

  const expandHandler = () => {
    defaultClickHandler();

    if (typeof onExpand === "function") {
      onExpand(original, !row.isExpanded); // isExpand value is not yet updated, that's why it's inverted
    }
  };

  const expandPadding = Array(depth)
    .fill()
    .map(() => <span className={classes.treePadding} key={uuidv4()} />);

  const expandIcon = canExpand && (
    <IconButton
      className={cx(classes.expand, {
        [classes.expandOpen]: isExpanded // todo: figure out how we can save previous state of expander to apply animations (each expander click changes rows completely)
      })}
      onClick={expandHandler}
      {...restToggleRowExpandedProps}
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
  row: PropTypes.object.isRequired,
  onExpand: PropTypes.func
};

export default Expander;
