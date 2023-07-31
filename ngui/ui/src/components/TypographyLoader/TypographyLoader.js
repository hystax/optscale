import React from "react";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const TypographyLoader = ({ linesCount = 1 }) =>
  [...Array(linesCount).keys()].map((line) => (
    <Typography key={line}>
      <Skeleton />
    </Typography>
  ));

TypographyLoader.propTypes = {
  linesCount: PropTypes.number
};

export default TypographyLoader;
