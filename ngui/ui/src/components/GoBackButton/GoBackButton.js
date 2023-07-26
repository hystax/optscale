import React from "react";
import ArrowBackOutlinedIcon from "@mui/icons-material/ArrowBack";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router-dom";
import IconButton from "components/IconButton";

const GoBackButton = () => {
  const navigate = useNavigate();
  return (
    <Box>
      <IconButton dataTestId="btn_go_back" icon={<ArrowBackOutlinedIcon />} onClick={() => navigate(-1)} />
    </Box>
  );
};

export default GoBackButton;
