import React from "react";
import ApiSuccessMessage from "components/ApiSuccessMessage";
import { number, select } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ApiSuccessMessage`
};

export const FE0000 = () => <ApiSuccessMessage successCode="FE0000" />;
export const FE0001 = () => <ApiSuccessMessage successCode="FE0001" />;
export const FE0002 = () => <ApiSuccessMessage successCode="FE0002" params={[number("Resources number", 1)]} />;
export const FE0003 = () => <ApiSuccessMessage successCode="FE0003" />;
export const FE0004 = () => (
  <ApiSuccessMessage
    successCode="FE0004"
    params={[select("Action type", ["decline", "accept", "cancel", "other"], "decline")]}
  />
);
export const FE0005 = () => <ApiSuccessMessage successCode="FE0005" params={[number("Employees number", 1)]} />;
