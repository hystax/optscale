import React, { useEffect, useState } from "react";
import Typography from "@mui/material/Typography";
import { useMeasure } from "@nivo/core";
import PropTypes from "prop-types";

// Empiric ???
const TOOLTIP_OFFSET = 14;

const ChartTooltip = ({ bandData, renderTooltipBody, barsCount }) => {
  const [measureRef, bounds] = useMeasure();

  const [x, setX] = useState(0);
  const [y, setY] = useState(0);

  const isLeftHalf = (bandData?.index ?? 0) < barsCount / 2;

  useEffect(() => {
    setX(isLeftHalf ? TOOLTIP_OFFSET : -bounds.width - TOOLTIP_OFFSET);
    setY(-bounds.height / 2);
  }, [bounds.width, bounds.height, isLeftHalf]);

  return (
    <div
      ref={measureRef}
      style={{
        position: "absolute",
        pointerEvents: "none",
        left: x,
        top: y,
        // Without this style rule, the tooltip wraps the text incorrectly when isLeftHalf is true.
        // For the bars on the right everything is displayed correclty. ¯\_(ツ)_/¯
        width: "max-content"
      }}
    >
      <Typography
        sx={(theme) => ({
          background: theme.palette.common.white,
          borderRadius: theme.spacing(0.25),
          boxShadow: "rgba(0, 0, 0, 0.25) 0px 1px 2px",
          paddingTop: theme.spacing(0.5),
          paddingBottom: theme.spacing(0.5),
          paddingLeft: theme.spacing(1),
          paddingRight: theme.spacing(1)
        })}
      >
        {renderTooltipBody(bandData)}
      </Typography>
    </div>
  );
};

ChartTooltip.propTypes = {
  bandData: PropTypes.object.isRequired,
  renderTooltipBody: PropTypes.func.isRequired,
  barsCount: PropTypes.number.isRequired
};

export default ChartTooltip;
