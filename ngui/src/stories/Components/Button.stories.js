import React from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Tooltip from "components/Tooltip";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import { select, boolean, text } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Button`
};

const colorOptions = {
  info: "info",
  inherit: "inherit",
  primary: "primary",
  success: "success",
  error: "error"
};

const sizeOptions = {
  small: "small",
  medium: "medium",
  large: "large"
};

const variantOptions = {
  text: "text",
  outlined: "outlined",
  contained: "contained"
};

export const basic = () => <Button messageId="add" />;
export const withIcon = () => <Button messageId="add" startIcon={<AddOutlinedIcon />} />;
export const withOnClick = () => <Button messageId="add" onClick={() => console.log("Button clicked")} />;
export const lowercase = () => <Button messageId="add" uppercase={false} />;
export const withTooltip = () => (
  <Tooltip title={<FormattedMessage id="add" />}>
    <Button messageId="add" />
  </Tooltip>
);
export const disabled = () => <Button messageId="add" disabled />;
export const withKnobs = () => (
  <Button
    messageId={text("messageId", "add")}
    startIcon={boolean("with icon", false) ? <AddOutlinedIcon /> : null}
    uppercase={boolean("uppercase", false)}
    onClick={() => console.log("Button clicked")}
    size={select("size", sizeOptions, "small")}
    variant={select("variant", variantOptions, "outlined")}
    disabled={boolean("disabled", false)}
    color={select("color", colorOptions, "info")}
  />
);
