import { useState } from "react";
import { useTheme } from "@mui/material/styles";
import GoogleMapReact from "google-map-react";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import MapMarker from "components/MapMarker";
import useGeoClusterer from "hooks/useGeoClusterer";
import { isEmpty } from "utils/arrays";
import { getEnvironmentVariable } from "utils/env";
import { apiIsLoaded, REGION_EXPENSES_HEIGHT } from "utils/maps";

const RegionExpensesMap = ({ markers, defaultZoom, defaultCenter, startDateTimestamp, endDateTimestamp }) => {
  const theme = useTheme();
  const [zoom, setZoom] = useState(defaultZoom);
  const onZoomChange = (newZoomValue) => setZoom(newZoomValue);
  const markersWithClusters = useGeoClusterer(
    markers.filter(({ type }) => type),
    zoom
  );

  const key = getEnvironmentVariable("VITE_GOOGLE_MAP_API_KEY");

  return !isEmpty(markersWithClusters) ? (
    <div style={{ height: `${REGION_EXPENSES_HEIGHT}px`, width: "100%" }}>
      {!key && <InlineSeverityAlert messageId="googleMapsIsNotConfigured" />}
      <GoogleMapReact
        bootstrapURLKeys={{ key }}
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

export default RegionExpensesMap;
