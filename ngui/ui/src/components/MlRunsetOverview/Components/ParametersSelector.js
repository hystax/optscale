import React from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import { ListItemText, MenuItem } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Checkbox from "components/Checkbox";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import { isEmpty as isEmptyArray } from "utils/arrays";

const Title = ({ messageId }) => (
  <MenuItem style={{ pointerEvents: "none" }}>
    <ListItemText primary={<FormattedMessage id={messageId} />} />
  </MenuItem>
);

const ParametersSelector = ({
  hyperparametersDimensionsNames,
  goalDimensionsNames,
  getGoalDimensionName,
  selected,
  onChange
}) => {
  const isItemSelected = (item) => selected.includes(item);

  const removeItemFromSelected = (item) => selected.filter((selectedItem) => selectedItem !== item);

  const handleChange = (item) => {
    const newSelected = isItemSelected(item) ? removeItemFromSelected(item) : [...selected, item];

    onChange(newSelected);
  };

  const renderItems = (items, getText) =>
    items.map((item) => (
      <MenuItem key={item} value={item} onClick={() => handleChange(item)}>
        <Checkbox size="small" checked={isItemSelected(item)} />
        <ListItemText primary={getText(item)} />
      </MenuItem>
    ));

  return (
    <Popover
      label={<IconButton icon={<SettingsIcon fontSize="small" />} />}
      menu={
        <>
          {isEmptyArray(hyperparametersDimensionsNames) ? null : (
            <>
              <Title messageId="hyperparameters" />
              {renderItems(hyperparametersDimensionsNames, (item) => item)}
            </>
          )}
          {isEmptyArray(goalDimensionsNames) ? null : (
            <>
              <Title messageId="goals" />
              {renderItems(goalDimensionsNames, (item) => getGoalDimensionName(item))}
            </>
          )}
        </>
      }
    />
  );
};

export default ParametersSelector;
