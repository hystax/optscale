import { CircularProgress } from "@mui/material";
import Backdrop from "components/Backdrop";

const BookingsCalendarLoader = ({ children }) => (
  <div style={{ position: "relative" }}>
    <Backdrop customClass="contentLoader">
      <CircularProgress />
    </Backdrop>
    {children}
  </div>
);

export default BookingsCalendarLoader;
