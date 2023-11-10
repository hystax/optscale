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

export default TrafficMapMarker;
