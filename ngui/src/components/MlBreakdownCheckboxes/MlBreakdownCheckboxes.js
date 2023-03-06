import React from "react";
import { FormControlLabel, Skeleton } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Checkbox from "components/Checkbox";
import Tooltip from "components/Tooltip";

const MlBreakdownCheckboxes = ({ selectedBreakdowns, colorsMap, breakdownConfig, onChange, isLoading }) =>
  isLoading ? (
    <Skeleton width="100%">
      <Checkbox />
    </Skeleton>
  ) : (
    Object.entries(breakdownConfig).map(([name, { renderBreakdownName, isNotImplemented }]) => (
      <Tooltip key={name} title={isNotImplemented ? <FormattedMessage id="comingSoon" /> : undefined}>
        <FormControlLabel
          control={
            <Checkbox
              disabled={isNotImplemented}
              checked={selectedBreakdowns.includes(name)}
              onChange={({ target: { checked: newChecked } }) => onChange(name, newChecked)}
              cssColor={colorsMap[name]}
            />
          }
          label={renderBreakdownName()}
        />
      </Tooltip>
    ))
  );

MlBreakdownCheckboxes.propTypes = {
  selectedBreakdowns: PropTypes.array.isRequired,
  colorsMap: PropTypes.object.isRequired,
  breakdownConfig: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default MlBreakdownCheckboxes;
