import CircularProgress from "@mui/material/CircularProgress";
import Backdrop from "components/Backdrop";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Backdrop`
};

export const basic = () => (
  <Backdrop>
    <CircularProgress />
  </Backdrop>
);
