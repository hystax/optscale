import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import { CLOUD_ACCOUNT_TYPE } from "utils/constants";

const MapLegend = ({ markers }) => {
  const uniqueTypes = [...new Map(markers.map((item) => [item.type, item])).values()].filter((item) => item.type);

  return (
    <>
      {uniqueTypes.map(({ type, color }) => (
        <Box key={`legend-${type}`} display="inline-flex" mr={2}>
          <Typography component="span">
            <CircleLabel textFirst={false} figureColor={color} label={<FormattedMessage id={CLOUD_ACCOUNT_TYPE[type]} />} />
          </Typography>
        </Box>
      ))}
    </>
  );
};

MapLegend.propTypes = {
  markers: PropTypes.array.isRequired
};

export default MapLegend;
