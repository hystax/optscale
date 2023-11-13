import Box from "@mui/material/Box";
import IconError from "components/IconError";

const SomethingWentWrong = () => (
  <Box height="100%" display="flex" alignItems="center">
    <IconError messageId="somethingWentWrong" />
  </Box>
);

export default SomethingWentWrong;
