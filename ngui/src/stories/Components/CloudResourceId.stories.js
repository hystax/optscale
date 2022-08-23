import React from "react";
import CloudResourceId from "components/CloudResourceId";
import { text } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/CloudResourceId`
};

export const awsResourceLink = () => (
  <CloudResourceId resourceId="46d16706-da10-4700-951b-fc9b5dd13c6b" cloudResourceId="i-11111111111111111" />
);

export const azureResourceLink = () => (
  <CloudResourceId
    resourceId="46d16706-da10-4700-951b-fc9b5dd13c6b"
    cloudResourceId="/subscriptions/46d16706-da10-4700-951b-fc9b5dd13c6b/randomname/randomname/providers/microsoft.randomname/randomipaddresses/random-ip"
  />
);

export const withKnobs = () => (
  <CloudResourceId
    resourceId={"46d16706-da10-4700-951b-fc9b5dd13c6b"}
    cloudResourceId={text(
      "cloudResourceId",
      "/subscriptions/46d16706-da10-4700-951b-fc9b5dd13c6b/randomname/randomname/providers/microsoft.randomname/randomipaddresses/random-ip"
    )}
  />
);
