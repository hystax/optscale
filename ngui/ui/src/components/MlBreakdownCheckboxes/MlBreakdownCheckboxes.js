import React from "react";
import { FormControlLabel, Skeleton } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Checkbox from "components/Checkbox";
import Tooltip from "components/Tooltip";

const MlBreakdownCheckboxes = ({
  selectedBreakdowns,
  colorsMap,
  breakdownConfig,
  onAddBreakdown,
  onRemoveBreakdown,
  isLoading
}) =>
  isLoading ? (
    <Skeleton width="100%">
      <Checkbox />
    </Skeleton>
  ) : (
    breakdownConfig.map(({ name, renderBreakdownName, isNotImplemented }) => (
      <Tooltip key={name} title={isNotImplemented ? <FormattedMessage id="comingSoon" /> : undefined}>
        <FormControlLabel
          control={
            <Checkbox
              disabled={isNotImplemented}
              checked={selectedBreakdowns.includes(name)}
              onChange={({ target: { checked } }) => {
                if (checked) {
                  onAddBreakdown(name);
                } else {
                  onRemoveBreakdown(name);
                }
              }}
              cssColor={colorsMap[name]}
            />
          }
          label={renderBreakdownName()}
        />
      </Tooltip>
    ))
  );

MlBreakdownCheckboxes.propTypes = {
  selectedBreakdowns: PropTypes.array,
  colorsMap: PropTypes.object,
  breakdownConfig: PropTypes.object,
  onAddBreakdown: PropTypes.func,
  onRemoveBreakdown: PropTypes.func,
  isLoading: PropTypes.bool
};

export default MlBreakdownCheckboxes;
