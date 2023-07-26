import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import CopyText from "components/CopyText";
import useStyles from "./CodeBlock.styles";

const CodeBlock = ({ text }) => {
  const { classes } = useStyles();

  return (
    <Box className={classes.wrapper}>
      <pre className={classes.codeBlock}>{text}</pre>
      <CopyText text={text} />
    </Box>
  );
};

CodeBlock.propTypes = {
  text: PropTypes.string.isRequired
};

export default CodeBlock;
