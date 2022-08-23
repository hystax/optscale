import React from "react";
import { select, text } from "@storybook/addon-knobs";
import CopyText from "components/CopyText";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/CopyText`
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
  caption: "caption",
  button: "button",
  overline: "overline",
  inherit: "inherit"
};

export const basic = () => <CopyText text="CopyText">CopyText</CopyText>;

export const withKnobs = () => {
  return (
    <CopyText
      text={text("text", "message")}
      variant={select("variant", variantOptions, "body2")}
      copyIconType={select("copyIconType", ["static", "animated"], "static")}
    >
      {text("text", "message")}
    </CopyText>
  );
};
