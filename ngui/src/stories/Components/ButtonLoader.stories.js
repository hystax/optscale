import React from "react";
import { text, boolean, select } from "@storybook/addon-knobs";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ButtonLoader from "components/ButtonLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonLoader`
};

const action = () => {
  console.log("Action");
};

const colorOptions = {
  info: "info",
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

export const basic = () => (
  <ButtonLoader
    isLoading={boolean("isLoading", true)}
    disabled={boolean("disabled", false)}
    messageId={text("text", "checkConnection")}
    size={select("size", sizeOptions, "small")}
    variant={select("variant", variantOptions, "outlined")}
    color={select("color", colorOptions, "info")}
    onClick={action}
  />
);

export const withIcon = () => (
  <ButtonLoader
    startIcon={<AddOutlinedIcon />}
    isLoading={boolean("isLoading", true)}
    disabled={boolean("disabled", false)}
    messageId={text("text", "checkConnection")}
    size={select("size", sizeOptions, "small")}
    variant={select("variant", variantOptions, "outlined")}
    color={select("color", colorOptions, "info")}
    onClick={action}
  />
);
