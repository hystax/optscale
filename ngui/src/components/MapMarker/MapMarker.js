import React, { useState } from "react";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getResourcesExpensesUrl } from "urls";
import { CLOUD_ACCOUNT_TYPE, REGION_FILTER, FORMATTED_MONEY_TYPES, ONE_CENT } from "utils/constants";
import { MAP_MARKER_FONT_SIZE_IN_PX } from "utils/fonts";
import { calculateDiameter } from "utils/maps";
import useStyles from "./MapMarker.styles";

const tooltipContent = ({ cloudType, value, region, startDateTimestamp, endDateTimestamp, intl, classes }) => (
  <div className={classes.markerTooltip}>
    <KeyValueLabel messageId={CLOUD_ACCOUNT_TYPE[cloudType]} value={region} />
    <KeyValueLabel messageId="expenses" value={value} />
    <Link
      to={getResourcesExpensesUrl({
        computedParams: `${REGION_FILTER}=${region}`,
        sStartDate: startDateTimestamp,
        sEndDate: endDateTimestamp
      })}
      component={RouterLink}
    >
      {intl.formatMessage({ id: "showResources" })}
    </Link>
  </div>
);

const MapMarker = ({ cloudType, region, value, startDateTimestamp, endDateTimestamp, color }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const intl = useIntl();
  const theme = useTheme();
  const { classes, cx } = useStyles();
  const { currencySymbol } = useOrganizationInfo();

  const fontSize = theme.typography.pxToRem(MAP_MARKER_FONT_SIZE_IN_PX);
  const borderColor = color || theme.palette.info.light;

  const diameter = calculateDiameter(value, MAP_MARKER_FONT_SIZE_IN_PX, currencySymbol);

  const markerTooltipWrapperClasses = cx(classes.markerTooltipWrapper, showTooltip ? classes.markerTooltipWrapperShow : "");

  return (
    <>
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={classes.marker}
        style={{
          display: "flex",
          cursor: "pointer",
          color: theme.palette.text.primary,
          fontWeight: "bold",
          borderRadius: "50% 50% 50% 0",
          overflow: "hidden",
          justifyContent: "center",
          alignItems: "center",
          width: diameter,
          height: diameter,
          border: `4px solid ${borderColor}`,
          backgroundColor: theme.palette.common.white,
          fontSize,
          position: "absolute",
          left: -diameter / 2,
          top: -diameter - diameter / 4,
          transform: "rotate(-45deg)"
        }}
      >
        <span style={{ transform: "rotate(45deg)" }}>
          {value > ONE_CENT && <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />}
        </span>
      </div>
      <div
        className={markerTooltipWrapperClasses}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {tooltipContent({
          cloudType,
          value: <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMMON} />,
          region,
          startDateTimestamp,
          endDateTimestamp,
          intl,
          classes
        })}
      </div>
    </>
  );
};

MapMarker.propTypes = {
  cloudType: PropTypes.string.isRequired,
  region: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  startDateTimestamp: PropTypes.number.isRequired,
  endDateTimestamp: PropTypes.number.isRequired,
  color: PropTypes.string
};

export default MapMarker;
