import { ONE_CENT } from "utils/constants";

export const REGION_EXPENSES_HEIGHT = 750;
export const TRAFFIC_EXPENSES_HEIGHT = 650;
export const EXTERNAL_LAT = 73;
export const EXTERNAL_LON = 25;
export const INTER_REGION_LAT = -47;
export const INTER_REGION_LON = 25;
export const INTER_REGION_NAME = "Inter-Region";

// Return map bounds based on list of markers
const getMapBounds = (map, maps, markers) => {
  const bounds = new maps.LatLngBounds();
  markers.map((marker) => bounds.extend(new maps.LatLng(marker.latitude, marker.longitude)));
  return bounds;
};

// Re-center map when resizing the window
const bindResizeListener = (map, maps, bounds) => {
  maps.event.addDomListenerOnce(map, "idle", () => {
    maps.event.addDomListener(window, "resize", () => {
      map.fitBounds(bounds);
    });
  });
};

export const apiIsLoaded = (map, maps, markers) => {
  // Get bounds by our markers
  const bounds = getMapBounds(map, maps, markers);
  // Fit map to bounds
  map.fitBounds(bounds);
  // Bind the resize listener
  bindResizeListener(map, maps, bounds);
};

// Calculate diameter of a marker
export const calculateDiameter = (value, fontSizeInPx, currencySymbol) =>
  value >= ONE_CENT ? 4 * fontSizeInPx + Math.log2(value) + currencySymbol.length * 4 : 15;
