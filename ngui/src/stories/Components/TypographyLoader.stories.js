import React from "react";
import { select, number } from "@storybook/addon-knobs";
import TypographyLoader from "components/TypographyLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/TypographyLoader`
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

export const basic = () => <TypographyLoader variant="body1" linesCount={1} />;

export const withKnobs = () => (
  <TypographyLoader variant={select("variant", variantOptions, "body1")} linesCount={number("linesCount", 1)} />
);
