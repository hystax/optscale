import Box from "@mui/material/Box";
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

export default Error;
