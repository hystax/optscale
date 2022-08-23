import React, { useState, forwardRef } from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ExpandMoreOutlinedIcon from "@mui/icons-material/ExpandMoreOutlined";
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import FormHelperText from "@mui/material/FormHelperText";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import IconButton from "components/IconButton";
import { capitalize } from "utils/strings";
import useStyles from "./Selector.styles";

const renderMenuItemIcon = (item, iconDefinition) => {
  const { component: IconComponent = Icon, getComponentProps = {} } = iconDefinition;
  return <IconComponent color="inherit" hasRightMargin {...getComponentProps(item)} />;
};

const renderMenuItem = (item, menuItemIcon) =>
  menuItemIcon ? (
    <>
      {renderMenuItemIcon(item, menuItemIcon)}
      {item.name}
    </>
  ) : (
    item.name
  );

const Selector = forwardRef(
  (
    {
      data,
      labelId,
      customClass,
      onChange,
      children,
      helperText,
      error = false,
      required = false,
      breakpoint = "sm",
      menuItemIcon,
      dataTestId,
      isMobile = false,
      fullWidth = false,
      readOnly,
      shrinkLabel = undefined,
      sx = {},
      ...rest
    },
    ref
  ) => {
    const { classes, cx } = useStyles();
    const [open, setOpen] = useState(false);

    const handleClose = () => {
      setOpen(false);
    };

    const handleOpen = () => {
      setOpen(true);
    };

    const handleChange = (event, child) => {
      const {
        props: { name }
      } = child;

      const { value } = event.target;
      // This prevents potentially saving 'undefined' into storage or/and settings it as selected
      if (value) {
        onChange(event.target.value, name);
      }
    };

    const { items: targetItems = [], selected } = data;
    const selectedItem = targetItems.some((item) => item.value === selected) ? selected : "";

    const getMenuItemClasses = ({ isRoot, value }) =>
      cx(isRoot ? classes.menuTitle : classes.menuItem, selectedItem !== value ? classes.notSelectedItem : "");

    const selectionList = (items) =>
      items.map((item) => {
        const { value, key, isRoot, customItem, dataTestId: menuItemDataTestId, name, disabled, onClick } = item;
        const menuItemProps = {
          // TODO: There is always a value, but not an id for some cases, should migrate to 'key' field eventually
          key: `menuItem-${value || key}`,
          value: isRoot || customItem ? null : value,
          className: getMenuItemClasses({ isRoot, value }),
          "data-test-id": menuItemDataTestId,
          name, // Name is used as the second parameter in the onChange handler, name is used when a selector has a read-only mode.
          disabled,
          onClick
        };

        return (
          <MenuItem key={menuItemProps.key} {...menuItemProps}>
            {customItem || renderMenuItem(item, menuItemIcon)}
          </MenuItem>
        );
      });

    const formControlClasses = cx(
      classes.selector,
      isMobile ? classes["sectionDesktop".concat(capitalize(breakpoint))] : "",
      customClass || ""
    );

    const label = labelId ? <FormattedMessage id={labelId} /> : null;

    return (
      <>
        <FormControl fullWidth={fullWidth} variant="outlined" className={formControlClasses} error={error} sx={sx}>
          {label && (
            <InputLabel shrink={shrinkLabel} id={`${labelId}-selector-label`} required={required}>
              {label}
            </InputLabel>
          )}
          <Select
            notched={shrinkLabel}
            data-test-id={dataTestId}
            value={selectedItem}
            label={label}
            classes={{
              root: cx(classes.selectRoot, rest.classes?.root),
              icon: rest.endAdornment ? classes.iconPositionWithAdornment : ""
            }}
            IconComponent={readOnly ? () => null : ArrowDropDownIcon}
            readOnly={readOnly}
            onChange={handleChange}
            inputRef={ref}
            {...rest}
          >
            {selectionList(targetItems)}
          </Select>
          {helperText ? <FormHelperText>{helperText}</FormHelperText> : null}
        </FormControl>
        {isMobile ? (
          <Box component="div" alignItems="center" className={classes["sectionMobile".concat(capitalize(breakpoint))]}>
            {children || null}
            <IconButton
              icon={<ExpandMoreOutlinedIcon />}
              customClass={classes.button}
              onClick={readOnly ? undefined : handleOpen}
            />
            <Select
              data-test-id={dataTestId}
              className={classes.mobileSelect}
              value={selectedItem}
              label={label}
              open={open}
              onClose={handleClose}
              onChange={handleChange}
              ref={ref}
              {...rest}
            >
              {selectionList(targetItems)}
            </Select>
          </Box>
        ) : null}
      </>
    );
  }
);

Selector.propTypes = {
  data: PropTypes.shape({
    selected: PropTypes.string,
    items: PropTypes.array // [ {id: number, name:"string", value:"string", isRoot: bool}, ... ]
  }).isRequired,
  sx: PropTypes.object,
  labelId: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  fullWidth: PropTypes.bool,
  customClass: PropTypes.string,
  helperText: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.shape({
      type: PropTypes.oneOf([FormattedMessage])
    })
  ]),
  menuItemIcon: PropTypes.shape({
    component: PropTypes.elementType,
    componentProps: PropTypes.oneOfType([PropTypes.object, PropTypes.func])
  }),
  children: PropTypes.node,
  required: PropTypes.bool,
  error: PropTypes.bool,
  breakpoint: PropTypes.string,
  dataTestId: PropTypes.string,
  isMobile: PropTypes.bool,
  readOnly: PropTypes.bool,
  shrinkLabel: PropTypes.oneOf([undefined, true, false])
};

export default Selector;
