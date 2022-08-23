import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import IconError from "components/IconError";

const Error = ({ messageId }) => (
  <Box height="100%" display="flex" alignItems="center">
    <IconError messageId={messageId} />
  </Box>
);

Error.propTypes = {
  messageId: PropTypes.node.isRequired
};

export default Error;
