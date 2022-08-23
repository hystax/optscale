import React from "react";
import Brackets from "components/Brackets";
import { select, text, boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Brackets`
};

const typeOptions = {
  round: "round",
  curly: "curly",
  square: "square",
  angle: "angle"
};

export const basic = () => <Brackets />;

export const bold = () => <Brackets bold />;

export const withChildren = () => <Brackets>{"..."}</Brackets>;

export const withKnobs = () => (
  <Brackets bold={boolean("bold", false)} type={select("type", typeOptions)}>
    {text("children", "...")}
  </Brackets>
);
