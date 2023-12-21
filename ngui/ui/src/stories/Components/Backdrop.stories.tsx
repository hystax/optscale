import CircularProgress from "@mui/material/CircularProgress";
import Backdrop from "components/Backdrop";

export default {
  component: Backdrop
};

export const basic = () => (
  <Backdrop>
    <CircularProgress />
  </Backdrop>
);
