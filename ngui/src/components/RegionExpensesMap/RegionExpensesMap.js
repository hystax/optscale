import React, { useState } from "react";
import { useTheme } from "@mui/material/styles";
import GoogleMapReact from "google-map-react";
import PropTypes from "prop-types";
import MapMarker from "components/MapMarker";
import useGeoClusterer from "hooks/useGeoClusterer";
import { isEmpty } from "utils/arrays";
import { apiIsLoaded, REGION_EXPENSES_HEIGHT } from "utils/maps";

const RegionExpensesMap = ({ markers, defaultZoom, defaultCenter, startDateTimestamp, endDateTimestamp }) => {
  const theme = useTheme();
  const [zoom, setZoom] = useState(defaultZoom);
  const onZoomChange = (newZoomValue) => setZoom(newZoomValue);
  const markersWithClusters = useGeoClusterer(
    markers.filter(({ type }) => type),
    zoom
  );

  return !isEmpty(markersWithClusters) ? (
    <div style={{ height: `${REGION_EXPENSES_HEIGHT}px`, width: "100%" }}>
      <GoogleMapReact
        bootstrapURLKeys={{ key: process.env.REACT_APP_GOOGLE_MAP_API_KEY }}
        defaultCenter={defaultCenter}
        defaultZoom={defaultZoom}
        yesIWantToUseGoogleMapApiInternals
        onGoogleApiLoaded={({ map, maps }) => apiIsLoaded(map, maps, markersWithClusters)}
        options={{ styles: theme.palette.googleMap, minZoom: 2, maxZoom: 6 }}
        onZoomAnimationEnd={onZoomChange}
      >
        {markersWithClusters.map((marker) => (
          <MapMarker
            markerData={marker}
            key={`marker-${marker.id}-${marker.name}`}
            lat={marker.latitude}
            lng={marker.longitude}
            startDateTimestamp={startDateTimestamp}
            endDateTimestamp={endDateTimestamp}
          />
        ))}
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
