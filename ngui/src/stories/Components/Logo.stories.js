import React from "react";
import { boolean, select } from "@storybook/addon-knobs";
import { KINDS } from "stories";
import Logo from "components/Logo";

export default {
  title: `${KINDS.COMPONENTS}/Logo`
};

const sizeOptions = {
  small: "small",
  medium: "medium"
};

export const basic = () => <Logo />;

export const withKnobs = () => (
  <Logo active={boolean("active", false)} white={boolean("white", false)} size={select("size", sizeOptions, "medium")} />
);
