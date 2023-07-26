import React, { useState } from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";

const Image = ({ customClass, src, alt, dataTestId }) => {
  const [show, setShow] = useState(false);

  return (
    <Box data-test-id={dataTestId} display={show ? "contents" : "none"}>
      <img className={customClass} src={src} alt={alt} onLoad={() => setShow(true)} onError={() => setShow(false)} />
    </Box>
  );
};

Image.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.oneOfType([PropTypes.string, PropTypes.object]).isRequired,
  customClass: PropTypes.string,
  dataTestId: PropTypes.string
};

export default Image;
