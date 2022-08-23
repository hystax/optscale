import React from "react";
import Ellipsis from "components/Ellipsis";
import { select } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Ellipsis`
};

const variantOptions = {
  h1: "h1",
  h2: "h2",
  h3: "h3",
  h4: "h4",
  h5: "h5",
  h6: "h6",
  subtitle1: "subtitle1",
  subtitle2: "subtitle2",
  body1: "body1",
  body2: "body2",
  caption: "caption"
};

const componentOptions = {
  p: "p",
  div: "div",
  span: "span"
};

const classNameOptions = {
  default: "",
  insideBrackets: "insideBrackets"
};

export const basic = () => <Ellipsis />;

export const withKnobs = () => (
  <Ellipsis
    variant={select("variant", variantOptions, "subtitle2")}
    component={select("component", componentOptions, "span")}
    className={select("className", classNameOptions, "default")}
  />
);
