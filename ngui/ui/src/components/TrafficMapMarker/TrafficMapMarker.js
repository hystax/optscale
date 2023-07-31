import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import useStyles from "./TrafficMapMarker.styles";

const TrafficMapMarker = ({ type, lat, onClick }) => {
  const { classes } = useStyles();
  const positionClass = lat < 0 ? classes.markerBottom : classes.markerTop;
  return (
    <>
      <div onClick={() => onClick({ type })} className={`${classes.marker} ${positionClass}`}>
        <span>
          <FormattedMessage id={type} />
        </span>
      </div>
    </>
  );
};

TrafficMapMarker.propTypes = {
  type: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lng: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired
};

export default TrafficMapMarker;
