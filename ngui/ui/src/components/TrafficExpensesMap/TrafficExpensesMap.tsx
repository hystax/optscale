import { useCallback, useEffect, useMemo, useState } from "react";
import { GoogleMapsOverlay } from "@deck.gl/google-maps";
import { getViewStateForLocations } from "@flowmap.gl/data";
import { FlowmapLayer, PickingType } from "@flowmap.gl/layers";
import { Stack } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import GoogleMapReact from "google-map-react";
import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import FromToArrowLabel from "components/FromToArrowLabel";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import TrafficMapMarker from "components/TrafficMapMarker";
import { isEmptyArray } from "utils/arrays";
import { EXPENSES_MAP_OBJECT_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getEnvironmentVariable } from "utils/env";
import { SPACING_2 } from "utils/layouts";
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
  getFlowMagnitude: (flow) => flow.cost,
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
  maxTopFlowsDisplayNum: 1000,
};

function renderToExpenses(expenses) {
  return expenses.map((expense) => (
    <KeyValueLabel
      key={expense.to.name}
      keyText={expense.to.name}
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
                  totalUsage: <FormattedDigitalUnit value={object.location.totalUsage} baseUnit={SI_UNITS.GIGABYTE} />,
                }}
              />
            </Typography>
            {!isEmptyArray(object.location.expenses) && (
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
        ),
      };
    case PickingType.FLOW: {
      const flowSummary = object.origin.summary.filter(
        (datum) => datum.mapped_from === object.origin.name && datum.mapped_to === object.dest.name
      );

      const { flowTotalExpenses, flowTotalUsage } = flowSummary.reduce(
        (acc, datum) => {
          acc.flowTotalExpenses += datum.cost;
          acc.flowTotalUsage += datum.usage;
          return acc;
        },
        { flowTotalExpenses: 0, flowTotalUsage: 0 }
      );

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
                  totalExpenses: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={flowTotalExpenses} />,
                  totalUsage: <FormattedDigitalUnit value={flowTotalUsage} baseUnit={SI_UNITS.GIGABYTE} />,
                }}
              />
            </Typography>
            {flowSummary.length > 1 && (
              <Typography variant="body1" component="div">
                {flowSummary.map((datum) => (
                  <KeyValueLabel
                    key={`${datum.original_from} -> ${datum.original_to}`}
                    isBoldValue={false}
                    keyText={<FromToArrowLabel from={datum.original_from} to={datum.original_to} />}
                    value={
                      <FormattedMessage
                        id="value / value"
                        values={{
                          value1: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={datum.cost} />,
                          value2: <FormattedDigitalUnit value={datum.usage} baseUnit={SI_UNITS.GIGABYTE} />,
                        }}
                      />
                    }
                  />
                ))}
              </Typography>
            )}
          </>
        ),
      };
    }
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
        globalThis.innerHeight,
      ]);
    }
    setViewParams({
      ...locationViewState,
      defaultZoom,
      defaultCenter,
      minZoom: 2,
      maxZoom: 6,
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
        },
      }),
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

  const otherMarker = data?.otherLocations.length ? data?.otherLocations[0] : null;
  const intercontinentalMarker = data?.interContinental;
  const interRegionMarker = data?.interRegion;
  const externalMarker = data?.externalLocation;

  const key = getEnvironmentVariable("VITE_GOOGLE_MAP_API_KEY");

  return (
    <Stack spacing={SPACING_2}>
      {!key && (
        <div>
          <InlineSeverityAlert messageId="googleMapsIsNotConfigured" />
        </div>
      )}
      <div
        className={`flowmap-container ${UI_INITIAL.darkMode ? "dark" : "light"}`}
        style={{ height: `${TRAFFIC_EXPENSES_HEIGHT}px`, width: "100%", position: "relative" }}
      >
        <GoogleMapReact
          bootstrapURLKeys={{ key }}
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
          {otherMarker && (
            <TrafficMapMarker
              key={`marker-${otherMarker.id}-${otherMarker.name}`}
              lat={otherMarker.latitude}
              lng={otherMarker.longitude}
              type={EXPENSES_MAP_OBJECT_TYPES.OTHER_MARKER}
              onClick={onMapClick}
              width={80}
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
          {intercontinentalMarker && (
            <TrafficMapMarker
              key={`marker-${intercontinentalMarker.id}-${intercontinentalMarker.name}`}
              lat={intercontinentalMarker.latitude}
              lng={intercontinentalMarker.longitude}
              type={EXPENSES_MAP_OBJECT_TYPES.INTER_CONTINENTAL_MARKER}
              onClick={onMapClick}
            />
          )}
          {externalMarker && (
            <TrafficMapMarker
              key={`marker-${externalMarker.id}-${externalMarker.name}`}
              lat={externalMarker.latitude}
              lng={externalMarker.longitude}
              type={EXPENSES_MAP_OBJECT_TYPES.EXTERNAL_MARKER}
              width={80}
              onClick={onMapClick}
            />
          )}
        </GoogleMapReact>
        <div id="map-legend" style={{ visibility: "hidden" }}>
          {legend}
        </div>
        <div id="map-tooltip" className={classes.tooltip} style={{ display: tooltip.display, ...tooltip.position }}>
          {tooltip.content}
        </div>
      </div>
    </Stack>
  );
};

export default TrafficExpensesMap;
