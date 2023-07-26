import React from "react";
import Logo from "components/Logo";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Logo`,
  argTypes: {
    size: {
      name: "Size",
      control: "select",
      options: ["small", "medium"],
      defaultValue: "small"
    },
    active: { name: "Active", control: "boolean", defaultValue: false },
    white: { name: "White", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <Logo />;

export const withKnobs = (args) => <Logo active={args.active} white={args.white} size={args.size} />;
