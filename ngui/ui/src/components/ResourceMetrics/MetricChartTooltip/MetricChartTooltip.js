import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import KeyValueLabel from "components/KeyValueLabel";
import { unixTimestampToDateTime, EN_FULL_FORMAT } from "utils/datetime";

const MetricChartTooltip = ({ slice }) => {
  const timestamp = slice.points[0].data.x;

  const body = (
    <>
      <Typography gutterBottom style={{ fontWeight: "bold" }}>
        {unixTimestampToDateTime(timestamp, EN_FULL_FORMAT)}
      </Typography>
      {slice.points.map((point) => (
        <KeyValueLabel
          key={point.id}
          renderKey={() => (
            <CircleLabel figureColor={point.serieColor} label={<FormattedMessage id={point.serieId} />} textFirst={false} />
          )}
          value={point.data.yFormatted}
        />
      ))}
    </>
  );

  return body;
};

MetricChartTooltip.propTypes = {
  slice: PropTypes.object
};

export default MetricChartTooltip;
