import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";

const InfoRow = ({ title, icon, value }) => (
  <Box fontSize={15} display="flex" alignItems="center" mb={1}>
    {`${title}:`}
    <Box fontWeight="bold" ml={1} display="flex" alignItems="center">
      {icon}
      {value}
    </Box>
  </Box>
);

InfoRow.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  icon: PropTypes.node
};

export default InfoRow;
