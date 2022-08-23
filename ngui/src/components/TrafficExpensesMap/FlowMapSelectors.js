import FlowmapSelectors from "@flowmap.gl/data/dist/FlowmapSelectors";
import { scaleLinear } from "d3-scale";
import { createSelector } from "reselect";
import { EXTERNAL_LAT, EXTERNAL_LON, INTER_REGION_LAT, INTER_REGION_LON } from "utils/maps";

const isExternalLocation = (location) => location.latitude === EXTERNAL_LAT && location.longitude === EXTERNAL_LON;
const isInterRegion = (location) => location.latitude === INTER_REGION_LAT && location.longitude === INTER_REGION_LON;

const getFlowThicknessScale = (magnitudeExtent) => {
  if (!magnitudeExtent) return undefined;
  return scaleLinear()
    .range([0.1, 0.1])
    .domain([
      0,
      // should support diff mode too
      Math.max.apply(
        null,
        magnitudeExtent.map((x) => Math.abs(x || 0))
      )
    ]);
};

export default class FlowMapSelectors extends FlowmapSelectors {
  getFlowThicknessScale = createSelector(this.getFlowMagnitudeExtent, getFlowThicknessScale);

  getInCircleSizeGetter = createSelector(
    this.getLocationsForFlowmapLayer,
    this.getCircleSizeScale,
    this.getLocationTotals,
    (locations, circleSizeScale, locationTotals) => (locationId) => {
      const total = locationTotals?.get(locationId);
      const location = locations?.find((loc) => loc.id === locationId);
      if (isExternalLocation(location) || isInterRegion(location)) {
        return 0;
      }
      if (total && circleSizeScale) {
        let scale = circleSizeScale(Math.abs(total.outgoingCount));
        // minimum circle size
        if (scale < 3) {
          scale = 3;
        }
        return scale;
      }
      return 3;
    }
  );

  getOutCircleSizeGetter = createSelector(
    this.getLocationsForFlowmapLayer,
    this.getCircleSizeScale,
    this.getLocationTotals,
    (locations, circleSizeScale, locationTotals) => (locationId) => {
      const total = locationTotals?.get(locationId);
      const location = locations?.find((loc) => loc.id === locationId);
      if (isExternalLocation(location) || isInterRegion(location)) {
        return 0;
      }
      if (total && circleSizeScale) {
        return circleSizeScale(Math.abs(total.outgoingCount)) || 0;
      }
      return 0;
    }
  );

  getLayersData = createSelector(
    this.getLocationsForFlowmapLayer,
    this.getFlowsForFlowmapLayer,
    this.getFlowmapColorsRGBA,
    this.getLocationsForFlowmapLayerById,
    this.getLocationIdsInViewport,
    this.getInCircleSizeGetter,
    this.getOutCircleSizeGetter,
    this.getFlowThicknessScale,
    this.getAnimate,
    this.getLocationLabelsEnabled,
    (
      locations,
      flows,
      flowmapColors,
      locationsById,
      locationIdsInViewport,
      getInCircleSize,
      getOutCircleSize,
      flowThicknessScale,
      animationEnabled,
      locationLabelsEnabled
      // eslint-disable-next-line max-params
    ) => {
      const layersData = this._prepareLayersData(
        locations,
        flows,
        flowmapColors,
        locationsById,
        locationIdsInViewport,
        getInCircleSize,
        getOutCircleSize,
        flowThicknessScale,
        animationEnabled,
        locationLabelsEnabled
      );
      const currentColors = layersData.circleAttributes.attributes.getColor.value;
      locations.forEach((location, index) => {
        if (location.totalExpenses === 0) {
          // overriding destination points color
          currentColors[index * 4] = 74;
          currentColors[index * 4 + 1] = 180;
          currentColors[index * 4 + 2] = 238;
          currentColors[index * 4 + 3] = 255;
        }
      });
      return layersData;
    }
  );
}
