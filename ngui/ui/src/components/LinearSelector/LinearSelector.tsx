import { useState } from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Chip from "components/Chip";
import DashedTypography from "components/DashedTypography";
import KeyValueLabel from "components/KeyValueLabel";
import Popover from "components/Popover";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import useStyles from "./LinearSelector.styles";

const NONE = "none";

const MenuItemCheckbox = ({ checked }) => <Checkbox style={{ padding: "0.2rem" }} size="small" checked={checked} />;

const ItemLabel = ({ name, handleChange, dataTestId, displayedName, endAdornment = null }) => {
  const { classes } = useStyles();

  return (
    <DashedTypography onClick={handleChange} component="span" dataTestId={dataTestId} className={classes.label}>
      {displayedName || <FormattedMessage id={name} />}
      {endAdornment}
    </DashedTypography>
  );
};

const PopoverWrapper = ({ menuBody, buttons, label, labelDataTestId, handleClose }) => (
  <Popover
    anchorOrigin={{
      vertical: "bottom",
      horizontal: "left"
    }}
    transformOrigin={{
      vertical: "top",
      horizontal: "left"
    }}
    label={label}
    buttons={buttons}
    handleClose={handleClose}
    menu={
      <div
        style={{
          overflow: "auto",
          maxHeight: "350px",
          paddingTop: "8px",
          paddingBottom: "8px",
          minWidth: "100px"
        }}
      >
        {menuBody}
      </div>
    }
    dataTestIds={{
      label: labelDataTestId
    }}
  />
);

const PopoverItem = ({ items, handleChange, labelDataTestId, label, checkboxLabel = null, enableCheckbox = false }) => {
  const [checked, setChecked] = useState(false);
  const { classes } = useStyles();

  return (
    <PopoverWrapper
      label={label}
      menuBody={
        <>
          {enableCheckbox && (
            <MenuItem
              className={classes.checkboxMenuItem}
              onClick={() => setChecked((currentCheckedState) => !currentCheckedState)}
            >
              <MenuItemCheckbox checked={checked} />
              <ListItemText primary={checkboxLabel} />
            </MenuItem>
          )}
          {items.map(({ name: itemName, label: itemLabel, value: itemValue, dataTestId, type: itemType }) => (
            <MenuItem
              key={[itemName, itemValue].filter((value) => value !== undefined).join("")}
              onClick={() => {
                handleChange({ name: itemName, value: itemValue, checked, type: itemType });
              }}
              data-test-id={dataTestId}
            >
              {itemLabel}
            </MenuItem>
          ))}
        </>
      }
      labelDataTestId={labelDataTestId}
    />
  );
};

const MultiPopoverItem = ({ name, items, label, handleApply, values }) => {
  const [selectedItems, setSelectedItems] = useState(values);

  const handleItemClick = (value) => {
    setSelectedItems((prevState) => {
      if (prevState.includes(value)) {
        return prevState.filter((e) => e !== value);
      }
      return [...prevState, value];
    });
  };

  return (
    <PopoverWrapper
      label={label}
      buttons={[
        {
          messageId: "apply",
          variant: "contained",
          onClick: () => handleApply({ name, value: selectedItems }),
          closable: true,
          dataTestId: "apply_multi_popover_button"
        }
      ]}
      handleClose={() => setSelectedItems(values)}
      menuBody={
        <>
          {items.map(({ name: itemName, label: itemLabel, value: itemValue }) => (
            <MenuItem
              key={[itemName, itemValue].filter((value) => value !== undefined).join("")}
              onClick={() => handleItemClick(itemValue)}
            >
              <MenuItemCheckbox checked={selectedItems.includes(itemValue)} />
              {itemLabel}
            </MenuItem>
          ))}
        </>
      }
    />
  );
};

const PopoverLabelExpandIcon = ({ isOpen }) => {
  const { classes } = useStyles();

  const Icon = isOpen ? ArrowDropUpIcon : ArrowDropDownIcon;

  return <Icon className={classes.labelIcon} />;
};

const PopoverLabel = ({ name, displayedName, isOpen }) => (
  <ItemLabel name={name} displayedName={displayedName} endAdornment={<PopoverLabelExpandIcon isOpen={isOpen} />} />
);

const Item = ({
  type = LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
  name,
  enablePopoverCheckbox = false,
  checkboxLabel,
  value,
  handleChange,
  handleApply,
  items,
  dataTestId,
  displayedName,
  values
}) => {
  const Component = {
    [LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER]: () => (
      <MultiPopoverItem
        name={name}
        items={items}
        handleApply={handleApply}
        values={values.filter((el) => el.name === name).map((el) => el.value)}
        label={({ isOpen }) => <PopoverLabel name={name} displayedName={displayedName} isOpen={isOpen} />}
      />
    ),
    [LINEAR_SELECTOR_ITEMS_TYPES.POPOVER]: () => (
      <PopoverItem
        items={items}
        enableCheckbox={enablePopoverCheckbox}
        checkboxLabel={checkboxLabel}
        handleChange={handleChange}
        labelDataTestId={dataTestId}
        label={({ isOpen }) => <PopoverLabel name={name} displayedName={displayedName} isOpen={isOpen} />}
      />
    ),
    [LINEAR_SELECTOR_ITEMS_TYPES.TEXT]: () => (
      <ItemLabel
        name={name}
        displayedName={displayedName}
        handleChange={() => handleChange({ name, value })}
        dataTestId={dataTestId}
      />
    )
  }[type];

  return <Component />;
};

const PickedItem = ({ name, dataTestId = name, value, type, onDelete, displayedName, displayedValue }) => {
  const getChipLabel = () => {
    const nameDisplayed = displayedName || <FormattedMessage id={name} />;
    const valueDisplayed = displayedValue || value;
    const typographyVariant = "subtitle2";

    return [LINEAR_SELECTOR_ITEMS_TYPES.POPOVER, LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER].includes(type) ? (
      <KeyValueLabel
        renderKey={() => nameDisplayed}
        value={valueDisplayed}
        variant={typographyVariant}
        dataTestIds={{
          typography: `chip_${dataTestId}_typography`,
          key: `chip_${dataTestId}_key`,
          value: `chip_${dataTestId}_value`
        }}
      />
    ) : (
      <Typography component="div" variant={typographyVariant} data-test-id={`chip_${dataTestId}_label`}>
        {nameDisplayed}
      </Typography>
    );
  };
  return (
    <Chip
      label={getChipLabel()}
      dataTestIds={{
        chip: `chip_${dataTestId}`,
        deleteIcon: `btn_${dataTestId}_close`
      }}
      color="info"
      size="medium"
      variant="outlined"
      onDelete={onDelete}
    />
  );
};

const SelectorItems = ({ items, values, onChange, onApply }) =>
  items.reduce((selectorItems, itemDefinition) => {
    const { name, items: popoverItems, type } = itemDefinition;
    const isSelected = values.some(({ name: valueName }) => valueName === name);

    // skipping all selected items, except multiselector
    if (isSelected && type !== LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER) {
      return selectorItems;
    }

    let notSelectedPopoverItems = [];

    if (type === LINEAR_SELECTOR_ITEMS_TYPES.POPOVER) {
      const { name: selectedItemName, value: selectedItemValue } =
        values.find((valueObject) => valueObject.name === name) ?? {};

      notSelectedPopoverItems =
        selectedItemName === name ? popoverItems.filter((el) => el.value !== selectedItemValue) : popoverItems;

      // skip if there are no items left in the popover
      if (isEmptyArray(notSelectedPopoverItems)) {
        return selectorItems;
      }
    }

    if (type === LINEAR_SELECTOR_ITEMS_TYPES.MULTISELECT_POPOVER) {
      // Skip popover if there are no items
      if (isEmptyArray(popoverItems)) {
        return selectorItems;
      }
      notSelectedPopoverItems = popoverItems;
    }

    return [
      ...selectorItems,
      <Box data-test-id={`selector_${name}`} key={itemDefinition.name}>
        <Item
          {...itemDefinition}
          items={notSelectedPopoverItems}
          handleChange={({ name: itemName, value: itemValue, checked }) => {
            if (typeof onChange === "function") {
              onChange({ name: itemName, value: itemValue, checked });
            }
          }}
          handleApply={onApply}
          values={values}
        />
      </Box>
    ];
  }, []);

const LinearSelector = ({ value, label, items, onClear, onClearAll, onChange, onApply, dataTestIds = {} }) => {
  const { label: labelDataTestId } = dataTestIds;

  const getValuesArray = () => {
    if (isEmptyObject(value)) {
      return [];
    }

    return (Array.isArray(value) ? value : [value]).map((pickedValue) => {
      const {
        type: itemType,
        displayedName: itemDisplayedName,
        dataTestId
      } = items.find((item) => item.name === pickedValue.name);

      return {
        name: pickedValue.name,
        value: pickedValue.value,
        displayedName: pickedValue.displayedName || itemDisplayedName,
        displayedValue: pickedValue.displayedValue,
        type: itemType,
        dataTestId
      };
    });
  };

  const valuesArray = getValuesArray();

  const { classes } = useStyles();

  return (
    <Box className={classes.wrapper}>
      {label && (
        <Typography component="div" data-test-id={labelDataTestId}>
          {label}
          {": "}
        </Typography>
      )}
      {valuesArray.length === 0 ? (
        <Typography component="span">
          <FormattedMessage id={NONE} />
        </Typography>
      ) : (
        <>
          {valuesArray.map((pickedValue) => {
            const {
              name: itemName,
              value: itemValue,
              displayedValue: itemDisplayedValue,
              type: itemType,
              displayedName,
              dataTestId
            } = pickedValue;

            return (
              <PickedItem
                key={`${itemName}-${itemValue}`}
                name={itemName}
                dataTestId={dataTestId}
                // equal to node that was defined in "values" array (LinearSelector)
                // or to node that was defined as a displayedName in items
                // or <FormattedMessage id={name}/>
                displayedName={displayedName}
                displayedValue={itemDisplayedValue}
                value={itemValue}
                type={itemType}
                onDelete={
                  typeof onClear === "function" ? () => onClear({ filterName: itemName, filterValue: itemValue }) : undefined
                }
              />
            );
          })}
          {valuesArray.length > 1 && onClearAll ? (
            <Button
              dataTestId="btn_clear"
              dashedBorder
              startIcon={<DeleteOutlinedIcon />}
              onClick={onClearAll}
              messageId="clearFilters"
              color="error"
            />
          ) : null}
        </>
      )}
      <Divider
        component="span"
        style={{ marginLeft: "8px", marginRight: "8px", width: "2px" }}
        flexItem
        orientation="vertical"
      />
      <SelectorItems items={items} values={valuesArray} onApply={onApply} onChange={onChange} />
    </Box>
  );
};

export default LinearSelector;
