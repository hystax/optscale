import React from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { boolean } from "@storybook/addon-knobs";
import Dropdown from "components/Dropdown";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Dropdown`
};

const items = [
  {
    key: "pool",
    messageId: "pool",
    link: "#",
    type: "button"
  },
  {
    key: "employees",
    messageId: "employees",
    link: "#",
    type: "button"
  },
  {
    key: "overview-edit",
    messageId: "edit",
    link: "#",
    type: "button"
  }
];

const mobileItems = [
  {
    key: "overview-add",
    icon: <AddOutlinedIcon fontSize="small" />,
    messageId: "add",
    type: "popover",
    menu: {
      items: [
        {
          key: "pool",
          messageId: "pool",
          mobileMessageId: "add",
          link: "#"
        },
        {
          key: "employees",
          messageId: "employees",
          link: "#"
        }
      ]
    }
  }
];

export const asButton = () => <Dropdown trigger="button" items={items} messageId="add" icon={<AddOutlinedIcon />} />;

export const asButtonWithKnobs = () => (
  <Dropdown
    trigger="button"
    items={items}
    messageId="add"
    icon={boolean("With start icon:", true) ? <AddOutlinedIcon /> : null}
  />
);

export const asIconButton = () => <Dropdown trigger="iconButton" items={items} />;

export const mobile = () => <Dropdown trigger="iconButton" items={mobileItems} isMobile />;
