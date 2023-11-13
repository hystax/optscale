import { useState } from "react";
import Box from "@mui/material/Box";

const Image = ({ customClass, src, alt, dataTestId }) => {
  const [show, setShow] = useState(false);

  return (
    <Box data-test-id={dataTestId} display={show ? "contents" : "none"}>
      <img className={customClass} src={src} alt={alt} onLoad={() => setShow(true)} onError={() => setShow(false)} />
    </Box>
  );
};

export default Image;
