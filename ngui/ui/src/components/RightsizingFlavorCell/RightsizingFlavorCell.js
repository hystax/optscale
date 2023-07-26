import React from "react";
import PropTypes from "prop-types";
import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel";

const RightsizingFlavorCell = ({ flavorName, flavorCpu }) => (
  <CaptionedCell
    caption={{
      node: <KeyValueLabel messageId="cpu" value={flavorCpu} isBoldValue={false} variant="caption" />
    }}
  >
    {flavorName}
  </CaptionedCell>
);

RightsizingFlavorCell.propTypes = {
  flavorName: PropTypes.string.isRequired,
  flavorCpu: PropTypes.number.isRequired
};

export default RightsizingFlavorCell;
