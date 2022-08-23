import React from "react";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import { select, boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/IconButton`
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
  medium: "medium"
};

const edgeOptions = {
  false: false,
  end: "end",
  start: "start"
};

export const basic = () => <IconButton icon={<EditOutlinedIcon />} />;
export const withOnClick = () => <IconButton icon={<EditOutlinedIcon />} onClick={() => console.log("Button clicked")} />;
export const withTooltip = () => (
  <IconButton
    icon={<EditOutlinedIcon />}
    tooltip={{
      show: true,
      value: <FormattedMessage id="edit" />
    }}
  />
);
export const disabled = () => <IconButton icon={<EditOutlinedIcon />} disabled />;
export const withKnobs = () => (
  <IconButton
    icon={<EditOutlinedIcon />}
    disabled={boolean("disabled", false)}
    edge={select("edge", edgeOptions, false)}
    size={select("size", sizeOptions, "small")}
    color={select("color", colorOptions, "info")}
  />
);
