import React, { useCallback, useEffect, useMemo, useState } from "react";
import { GoogleMapsOverlay } from "@deck.gl/google-maps";
import { getViewStateForLocations } from "@flowmap.gl/data";
import { FlowmapLayer, PickingType } from "@flowmap.gl/layers";
import { useTheme } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import GoogleMapReact from "google-map-react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import FromToArrowLabel from "components/FromToArrowLabel";
import KeyValueLabel from "components/KeyValueLabel";
import TrafficMapMarker from "components/TrafficMapMarker";
import { isEmpty } from "utils/arrays";
import { EXPENSES_MAP_OBJECT_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getEnvironmentVariable } from "utils/env";
import { TRAFFIC_EXPENSES_HEIGHT } from "utils/maps";
import FlowMapDataProvider from "./FlowMapDataProvider";
import useStyles from "./TrafficExpensesMap.styles";

const layerProps = {
  getLocationId: (loc) => loc.id,
  getLocationLat: (loc) => loc.latitude,
  getLocationLon: (loc) => loc.longitude,
  getFlowOriginId: (flow) => flow.from.name,
  getLocationName: (loc) => loc.name,
  getFlowDestId: (flow) => flow.to.name,
  getFlowMagnitude: (flow) => flow.cost
};
let deckOverlay = new GoogleMapsOverlay();
const dataProvider = new FlowMapDataProvider(layerProps);

const currentColor = ["#A7E1F1", "#6CD3F5", "#A4DE34", "#ECEB1A", "#FCB315", "#F12426"];

const DEFAULT_TOOLTIP_STATE = { display: "none", position: { left: 0, top: 0 }, content: "" };

const UI_INITIAL = {
  darkMode: false,
  colorScheme: currentColor,
  highlightColor: "#ff9b29",
  opacity: 1.0,
  fadeEnabled: false,
  fadeOpacityEnabled: false,
  fadeAmount: 10,
  clusteringEnabled: false,
  clusteringAuto: true,
  clusteringLevel: 1,
  clusteringMethod: "HCA",
  animationEnabled: false,
  adaptiveScalesEnabled: false,
  locationTotalsEnabled: true,
  locationLabelsEnabled: false,
  maxTopFlowsDisplayNum: 1000
};

function renderToExpenses(expenses) {
  return expenses.map((expense) => (
    <KeyValueLabel
      key={expense.to.name}
      text={expense.to.name}
      value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={expense.cost} />}
    />
  ));
}

function getTooltipState(info) {
  if (!info) return DEFAULT_TOOLTIP_STATE;
  const { x, y, object } = info;
  const position = { left: x, top: y };
  switch (object?.type) {
    case PickingType.LOCATION:
      return {
        position,
        display: "block",
        content: (
          <>
            <Typography variant="caption" component="div">
              <strong>{object.name}</strong>
            </Typography>
            <Typography variant="caption" component="div">
              <FormattedMessage
                id="totalExpensesWithTotalExpensesAndCost"
                values={{
                  totalExpenses: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={object.location.totalExpenses} />,
                  totalUsage: <FormattedDigitalUnit value={object.location.totalUsage} baseUnit={SI_UNITS.GIGABYTE} />
                }}
              />
            </Typography>
            {!isEmpty(object.location.expenses) && (
              <>
                <Typography variant="caption" component="div">
                  <FormattedMessage id="to" />
                </Typography>
                <Typography variant="body1" component="div">
                  {renderToExpenses(object.location.expenses)}
                </Typography>
              </>
            )}
          </>
        )
      };
    case PickingType.FLOW:
      return {
        position,
        display: "block",
        content: (
          <>
            <Typography variant="caption" component="div">
              <FromToArrowLabel from={object.origin.id} to={object.dest.id} strong />
            </Typography>
            <Typography variant="caption" component="div">
              <FormattedMessage
                id="totalExpensesWithTotalExpensesAndCost"
                values={{
                  totalExpenses: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={object.flow.count} />,
                  totalUsage: (
                    <FormattedDigitalUnit
                      value={object.origin.expenses.find((expense) => expense.to.name === object.dest.id).usage}
                      baseUnit={SI_UNITS.GIGABYTE}
                    />
                  )
                }}
              />
            </Typography>
          </>
        )
      };
    default:
      return DEFAULT_TOOLTIP_STATE;
  }
}

const TrafficExpensesMap = ({ markers, defaultZoom, defaultCenter, onMapClick = () => {} }) => {
  const { classes } = useStyles();
  const [viewParams, setViewParams] = useState();
  const [data, setData] = useState();
  const [tooltip, setTooltip] = useState(DEFAULT_TOOLTIP_STATE);
  const [layers, setLayers] = useState([]);
  const [legendMax, setLegendMax] = useState(0);

  const theme = useTheme();

  useEffect(() => {
    if (markers.flows && markers.locations) {
      setData(markers);
      dataProvider.setFlowmapData(markers);
    }
  }, [markers]);

  useEffect(() => {
    let locationViewState = { latitude: defaultCenter.lat, longitude: defaultCenter.lng };
    if (data?.locations.length) {
      locationViewState = getViewStateForLocations(data.locations, (loc) => [loc.longitude, loc.latitude], [
        globalThis.innerWidth,
        globalThis.innerHeight
      ]);
    }
    setViewParams({
      ...locationViewState,
      defaultZoom,
      defaultCenter,
      minZoom: 2,
      maxZoom: 6
    });
  }, [data, defaultZoom, defaultCenter, setViewParams]);

  const refreshLegendMax = () => {
    const flows = dataProvider.getFlowsForFlowmapLayer() || [];
    setLegendMax(Math.max(0, ...flows.map((flow) => flow.count)));
  };

  const refreshLayers = useCallback(() => {
    setLayers([
      new FlowmapLayer({
        id: "my-flowmap-layer",
        dataProvider,
        ...layerProps,
        opacity: UI_INITIAL.opacity,
        pickable: true,
        darkMode: UI_INITIAL.darkMode,
        colorScheme: UI_INITIAL.colorScheme,
        fadeAmount: UI_INITIAL.fadeAmount,
        fadeEnabled: UI_INITIAL.fadeEnabled,
        fadeOpacityEnabled: UI_INITIAL.fadeOpacityEnabled,
        locationTotalsEnabled: UI_INITIAL.locationTotalsEnabled,
        locationLabelsEnabled: UI_INITIAL.locationLabelsEnabled,
        animationEnabled: UI_INITIAL.animationEnabled,
        clusteringEnabled: UI_INITIAL.clusteringEnabled,
        clusteringAuto: UI_INITIAL.clusteringAuto,
        clusteringLevel: UI_INITIAL.clusteringLevel,
        adaptiveScalesEnabled: UI_INITIAL.adaptiveScalesEnabled,
        highlightColor: UI_INITIAL.highlightColor,
        maxTopFlowsDisplayNum: UI_INITIAL.maxTopFlowsDisplayNum,
        onHover: (info) => setTooltip(getTooltipState(info)),
        onClick: (info) => {
          setTooltip(getTooltipState(null));
          onMapClick(info.object);
        }
      })
    ]);
    refreshLegendMax();
  }, [onMapClick]);

  useEffect(() => refreshLayers, [data, refreshLayers]);

  useEffect(() => deckOverlay.setProps({ layers }), [layers]);

  const legend = useMemo(
    () => (
      <>
        <div className={classes.legend} />
        <span>
          <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={0} />
        </span>
        <span style={{ float: "right" }}>
          <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={legendMax} />
        </span>
      </>
    ),
    [classes.legend, legendMax]
  );

  const onChange = () => {
    refreshLegendMax();
  };

  if (!viewParams) {
    return null;
  }

  const externalMarker = data?.externalLocations.length ? data?.externalLocations[0] : null;
  const interRegionMarker = data?.interRegion;

  return (
    <div
      className={`flowmap-container ${UI_INITIAL.darkMode ? "dark" : "light"}`}
      style={{ height: `${TRAFFIC_EXPENSES_HEIGHT}px`, width: "100%", position: "relative" }}
    >
      <GoogleMapReact
        bootstrapURLKeys={{ key: getEnvironmentVariable("REACT_APP_GOOGLE_MAP_API_KEY") }}
        defaultCenter={viewParams.defaultCenter}
        center={{ lat: viewParams.latitude, lng: viewParams.longitude }}
        defaultZoom={viewParams.defaultZoom}
        zoom={viewParams.zoom}
        options={{ styles: theme.palette.googleMap, minZoom: viewParams.minZoom, maxZoom: viewParams.maxZoom }}
        yesIWantToUseGoogleMapApiInternals
        onChange={onChange}
        onGoogleApiLoaded={({ map, maps }) => {
          const mapLegend = document.getElementById("map-legend");
          const mapTooltip = document.getElementById("map-tooltip");
          map.controls[maps.ControlPosition.BOTTOM_CENTER].push(mapLegend);
          map.controls[maps.ControlPosition.TOP_LEFT].push(mapTooltip);
          setLayers([]);
          deckOverlay.finalize();
          deckOverlay = new GoogleMapsOverlay();
          deckOverlay.setMap(map);
          refreshLayers();
        }}
      >
        {externalMarker && (
          <TrafficMapMarker
            key={`marker-${externalMarker.id}-${externalMarker.name}`}
            lat={externalMarker.latitude}
            lng={externalMarker.longitude}
            type={EXPENSES_MAP_OBJECT_TYPES.EXTERNAL_MARKER}
            onClick={onMapClick}
          />
        )}
        {interRegionMarker && (
          <TrafficMapMarker
            key={`marker-${interRegionMarker.id}-${interRegionMarker.name}`}
            lat={interRegionMarker.latitude}
            lng={interRegionMarker.longitude}
            type={EXPENSES_MAP_OBJECT_TYPES.INTER_REGION_MARKER}
            onClick={onMapClick}
          />
        )}
      </GoogleMapReact>
      <div id={"map-legend"} style={{ visibility: "hidden" }}>
        {legend}
      </div>
      <div id={"map-tooltip"} className={classes.tooltip} style={{ display: tooltip.display, ...tooltip.position }}>
        {tooltip.content}
      </div>
    </div>
  );
};

TrafficExpensesMap.propTypes = {
  markers: PropTypes.object.isRequired,
  defaultZoom: PropTypes.number.isRequired,
  defaultCenter: PropTypes.object.isRequired,
  onMapClick: PropTypes.func
};

export default TrafficExpensesMap;
