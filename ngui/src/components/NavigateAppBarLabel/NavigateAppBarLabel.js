import React from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";

const NavigateAppBarLabel = ({ to, label }) => {
  const navigate = useNavigate();

  return (
    <Typography
      variant="caption"
      onClick={() => navigate(to)}
      sx={{
        color: (theme) => theme.palette.info.main,
        textDecoration: "underline",
        ":hover": {
          cursor: "pointer"
        }
      }}
    >
      {label}
    </Typography>
  );
};

NavigateAppBarLabel.propTypes = {
  to: PropTypes.string.isRequired,
  label: PropTypes.node.isRequired
};

export default NavigateAppBarLabel;
