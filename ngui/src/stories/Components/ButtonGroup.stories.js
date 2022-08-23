import React from "react";
import { object, number } from "@storybook/addon-knobs";
import ButtonGroup from "components/ButtonGroup";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonGroup`
};

const buttons = [
  {
    id: "action",
    messageId: "action",
    action: (e) => console.log(e)
  },
  {
    id: "add",
    messageId: "add",
    action: (e) => console.log(e)
  },
  {
    id: "activity",
    messageId: "activity",
    action: (e) => console.log(e)
  }
];

export const oneAction = () => (
  <ButtonGroup
    activeButtonIndex={0}
    buttons={[
      {
        id: "action",
        messageId: "action",
        action: (e) => console.log(e)
      }
    ]}
  />
);
export const twoActions = () => (
  <ButtonGroup
    activeButtonIndex={0}
    buttons={[
      {
        id: "action",
        messageId: "action",
        action: (e) => console.log(e)
      },
      {
        id: "add",
        messageId: "add",
        action: (e) => console.log(e)
      }
    ]}
  />
);
export const threeActions = () => <ButtonGroup activeButtonIndex={0} buttons={buttons} />;
export const withKnobs = () => (
  <ButtonGroup activeButtonIndex={number("activeButtonIndex", 0)} buttons={object("buttons", buttons)} />
);
