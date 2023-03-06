import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import IconError from "components/IconError";

const Error = ({ messageId }) => (
  <Box
    sx={{
      height: "100vh",
      width: "100vw",
      position: "fixed",
      top: 0,
      left: 0,
      display: "flex",
      alignItems: "center",
      pointerEvents: "none"
    }}
  >
    <IconError messageId={messageId} />
  </Box>
);

Error.propTypes = {
  messageId: PropTypes.node.isRequired
};

export default Error;
