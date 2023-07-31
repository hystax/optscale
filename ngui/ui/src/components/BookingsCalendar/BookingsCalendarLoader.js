import React from "react";
import { CircularProgress } from "@mui/material";
import PropTypes from "prop-types";
import Backdrop from "components/Backdrop";

const BookingsCalendarLoader = ({ children }) => (
  <div style={{ position: "relative" }}>
    <Backdrop customClass="contentLoader">
      <CircularProgress />
    </Backdrop>
    {children}
  </div>
);

BookingsCalendarLoader.propTypes = {
  children: PropTypes.node.isRequired
};

export default BookingsCalendarLoader;
