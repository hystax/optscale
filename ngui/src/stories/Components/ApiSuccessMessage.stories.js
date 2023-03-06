import React from "react";
import ApiSuccessMessage from "components/ApiSuccessMessage";
import { KINDS } from "stories";
import { SETTINGS_TYPE } from "components/RecommendationSettings/RecommendationSettings";

const RECOMMENDATION_SETTINGS_TYPES = Object.values(SETTINGS_TYPE);

export default {
  title: `${KINDS.COMPONENTS}/ApiSuccessMessage`,
  argTypes: {
    resourceCount: { name: "FE06 Resource count", control: "number", defaultValue: 1 },
    totalResourceCount: { name: "FE06 Total resource count", control: "number", defaultValue: 10 },
    settingsUpdated: {
      name: "FE10 Setting updated",
      control: "select",
      options: RECOMMENDATION_SETTINGS_TYPES,
      defaultValue: RECOMMENDATION_SETTINGS_TYPES[0]
    },
    employeeCount: { name: "FE03 Employee count", control: "number", defaultValue: 1 },
    assignmentRuleName: { name: "FE07 Assignment rule name", control: "string", defaultValue: "Foo" }
  }
};

export const FE0000 = () => <ApiSuccessMessage successCode="FE0000" />;
export const FE0001 = () => <ApiSuccessMessage successCode="FE0001" />;
export const FE0003 = (args) => <ApiSuccessMessage successCode="FE0003" params={[args.employeeCount]} />;
export const FE0006 = (args) => (
  <ApiSuccessMessage successCode="FE0006" params={[args.resourceCount, args.totalResourceCount]} />
);
export const FE0007 = (args) => <ApiSuccessMessage successCode="FE0007" params={[args.assignmentRuleName]} />;
export const FE0008 = () => <ApiSuccessMessage successCode="FE0008" />;
export const FE0009 = () => <ApiSuccessMessage successCode="FE0009" />;
export const FE0010 = (args) => <ApiSuccessMessage successCode="FE0010" params={[args.settingsUpdated]} />;
