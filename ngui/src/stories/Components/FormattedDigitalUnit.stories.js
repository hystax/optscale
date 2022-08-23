import React from "react";
import { number, select } from "@storybook/addon-knobs";
import FormattedDigitalUnit, { IEC_UNITS, SI_UNITS, SYSTEM_OF_UNITS } from "components/FormattedDigitalUnit";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/FormattedDigitalUnit`
};

export const iecDigitalUnitWithKnobs = () => (
  <FormattedDigitalUnit value={number("value", 0)} baseUnit={select("baseUnit", IEC_UNITS)} />
);

export const siDigitalUnitWithKnobs = () => (
  <FormattedDigitalUnit value={number("value", 0)} baseUnit={select("baseUnit", SI_UNITS)} />
);
