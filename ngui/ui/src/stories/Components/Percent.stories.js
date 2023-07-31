import React from "react";
import Percent from "components/Percent";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Percent`,
  argTypes: {
    value: { name: "Value", control: "number", defaultValue: 4.2 }
  }
};

export const basic = () => <Percent value={5} />;

export const withKnobs = (args) => <Percent value={args.value} minimumFractionDigits={2} />;
