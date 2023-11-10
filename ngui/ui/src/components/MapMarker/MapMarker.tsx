import { useState } from "react";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Circle from "components/Circle";
import CircleLabel from "components/CircleLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getResourcesExpensesUrl } from "urls";
import { splitIntoTwoChunks } from "utils/arrays";
import { CLOUD_ACCOUNT_TYPE, REGION_FILTER, FORMATTED_MONEY_TYPES, ONE_CENT } from "utils/constants";
import { MAP_MARKER_FONT_SIZE_IN_PX } from "utils/fonts";
import { calculateDiameter } from "utils/maps";
import useStyles from "./MapMarker.styles";

const TotalLabel = ({ total, isCluster }) =>
  total > ONE_CENT || isCluster ? <FormattedMoney value={total} type={FORMATTED_MONEY_TYPES.COMPACT} /> : null;

const ClusterMarker = ({ setShowTooltip, total, items, fontSize, diameter, className }) => {
  const theme = useTheme();
  const uniqueColors = [...new Set(items.map(({ color }) => color || theme.palette.info.light))];

  return (
    <div
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      style={{
        width: diameter,
        height: diameter,
        fontSize
      }}
      className={className}
    >
      <TotalLabel total={total} isCluster />
      <div display="block">
        {uniqueColors.map((color) => (
          <span key={`micro-legend-${color}`}>
            <Circle color={color} />
          </span>
        ))}
      </div>
    </div>
  );
};

const SimpleMarker = ({ setShowTooltip, className, diameter, fontSize, borderColor, total }) => (
  <div
    onMouseEnter={() => setShowTooltip(true)}
    onMouseLeave={() => setShowTooltip(false)}
    className={className}
    style={{
      width: diameter,
      height: diameter,
      borderColor: `${borderColor}`,
      fontSize,
      left: -diameter / 2,
      top: -diameter - diameter / 4
    }}
  >
    <span style={{ transform: "rotate(45deg)" }}>
      <TotalLabel total={total} />
    </span>
  </div>
);

const TooltipItem = ({ children }) => {
  const { classes } = useStyles();
  return <div className={classes.tooltipItem}>{children}</div>;
};

const getTooltipContent = ({ markers, startDateTimestamp, endDateTimestamp }) => {
  const topLength = 5;

  const [top, others] = splitIntoTwoChunks(markers, topLength);
  const othersTotal = others.reduce((acc, { total }) => acc + total, 0);
  const showOther = markers.length > topLength;

  return (
    <>
      {top.map(({ id, type: cloudType, name: region, total: value, color }) => (
        <TooltipItem key={`tooltip-item-${id}-${region}`}>
          <KeyValueLabel
            renderKey={() => (
              <CircleLabel
                textFirst={false}
                figureColor={color}
                label={<FormattedMessage id={CLOUD_ACCOUNT_TYPE[cloudType]} />}
              />
            )}
            value={region}
          />
          <KeyValueLabel messageId="expenses" value={<FormattedMoney value={value} />} />
          <Link
            to={getResourcesExpensesUrl({
              computedParams: `${REGION_FILTER}=${region}`,
              sStartDate: startDateTimestamp,
              sEndDate: endDateTimestamp
            })}
            component={RouterLink}
          >
            <FormattedMessage id="showResources" />
          </Link>
        </TooltipItem>
      ))}
      {showOther && (
        <TooltipItem key={`tooltip-item-others`}>
          <KeyValueLabel
            text={<FormattedMessage id="otherRegions" />}
            value={<FormattedMoney value={othersTotal} type={FORMATTED_MONEY_TYPES.COMMON} />}
          />
        </TooltipItem>
      )}
    </>
  );
};

const MapMarker = ({ markerData, startDateTimestamp, endDateTimestamp }) => {
  const theme = useTheme();

  const { total, color = theme.palette.info.light, isCluster, items } = markerData;

  const [showTooltip, setShowTooltip] = useState(false);

  const { classes, cx } = useStyles();
  const { currencySymbol } = useOrganizationInfo();

  const fontSize = theme.typography.pxToRem(MAP_MARKER_FONT_SIZE_IN_PX);

  const diameter = calculateDiameter(isCluster ? Math.max(1, total) : total, MAP_MARKER_FONT_SIZE_IN_PX, currencySymbol);

  const markerTooltipWrapperClasses = cx(classes.markerTooltipWrapper, showTooltip ? classes.markerTooltipWrapperShow : "");

  const tooltipContent = getTooltipContent({ markers: items || [markerData], startDateTimestamp, endDateTimestamp });

  const markerProps = {
    total,
    fontSize,
    diameter,
    setShowTooltip,
    className: cx(classes.markerBase, isCluster ? classes.cluster : classes.marker)
  };

  return (
    <>
      {isCluster ? (
        <ClusterMarker items={items} className={cx(classes.markerBase, classes.cluster)} {...markerProps} />
      ) : (
        <SimpleMarker borderColor={color} className={cx(classes.marker, classes.markerBase)} {...markerProps} />
      )}
      <div
        className={markerTooltipWrapperClasses}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <div className={classes.markerTooltip}>{tooltipContent}</div>
      </div>
    </>
  );
};

export default MapMarker;
