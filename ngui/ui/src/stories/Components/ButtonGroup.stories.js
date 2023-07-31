import React from "react";
import ButtonGroup from "components/ButtonGroup";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonGroup`,
  argTypes: {
    activeButtonIndex: { name: "Active button index", control: "number", defaultValue: 0 }
  }
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

export const withKnobs = (args) => <ButtonGroup activeButtonIndex={args.activeButtonIndex} buttons={buttons} />;
