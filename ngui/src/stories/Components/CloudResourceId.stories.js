import React from "react";
import CloudResourceId from "components/CloudResourceId";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/CloudResourceId`,
  argTypes: {
    cloudResourceIdentifier: {
      name: "Cloud resource ID",
      control: "text",
      defaultValue:
        "/subscriptions/46d16706-da10-4700-951b-fc9b5dd13c6b/randomname/randomname/providers/microsoft.randomname/randomipaddresses/random-ip"
    }
  }
};

export const awsResourceLink = () => (
  <CloudResourceId resourceId="46d16706-da10-4700-951b-fc9b5dd13c6b" cloudResourceIdentifier="i-11111111111111111" />
);

export const azureResourceLink = () => (
  <CloudResourceId
    resourceId="46d16706-da10-4700-951b-fc9b5dd13c6b"
    cloudResourceIdentifier="/subscriptions/46d16706-da10-4700-951b-fc9b5dd13c6b/randomname/randomname/providers/microsoft.randomname/randomipaddresses/random-ip"
  />
);

export const withKnobs = (args) => (
  <CloudResourceId
    resourceId={"46d16706-da10-4700-951b-fc9b5dd13c6b"}
    cloudResourceIdentifier={argTypes.cloudResourceIdentifier}
  />
);
