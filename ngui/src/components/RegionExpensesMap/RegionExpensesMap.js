import React from "react";
import { useTheme } from "@mui/material/styles";
import GoogleMapReact from "google-map-react";
import PropTypes from "prop-types";
import MapMarker from "components/MapMarker";
import { isEmpty } from "utils/arrays";
import { apiIsLoaded, REGION_EXPENSES_HEIGHT } from "utils/maps";

const RegionExpensesMap = ({ markers, defaultZoom, defaultCenter, startDateTimestamp, endDateTimestamp }) => {
  const theme = useTheme();
  return !isEmpty(markers) ? (
    <div style={{ height: `${REGION_EXPENSES_HEIGHT}px`, width: "100%" }}>
      <GoogleMapReact
        bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_MAP_API_KEY }}
        defaultCenter={defaultCenter}
        defaultZoom={defaultZoom}
        yesIWantToUseGoogleMapApiInternals
        onGoogleApiLoaded={({ map, maps }) => apiIsLoaded(map, maps, markers)}
        options={{ styles: theme.palette.googleMap, minZoom: 2, maxZoom: 6 }}
      >
        {markers.map(
          (marker) =>
            marker.type && (
              <MapMarker
                key={`marker-${marker.id}-${marker.name}`}
                lat={marker.latitude}
                lng={marker.longitude}
                cloudType={marker.type}
                region={marker.name}
                value={marker.total}
                color={marker.color}
                startDateTimestamp={startDateTimestamp}
                endDateTimestamp={endDateTimestamp}
              />
            )
        )}
      </GoogleMapReact>
    </div>
  ) : null;
};

RegionExpensesMap.propTypes = {
  markers: PropTypes.array.isRequired,
  defaultZoom: PropTypes.number.isRequired,
  defaultCenter: PropTypes.object.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number
};

export default RegionExpensesMap;
