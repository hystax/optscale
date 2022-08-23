import React from "react";
import ButtonSwitch from "components/ButtonSwitch";
import CloudIcon from "@mui/icons-material/Cloud";
import BusinessIcon from "@mui/icons-material/Business";
import PeopleIcon from "@mui/icons-material/People";
import { text, select } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonSwitch`
};

const buttons = [
  { messageId: "cloud", link: "/", icon: <CloudIcon /> },
  { messageId: "pool", link: "/", icon: <BusinessIcon /> },
  { messageId: "owner", link: "/", icon: <PeopleIcon /> }
];

const iconsArray = [<CloudIcon key={1} />, <BusinessIcon key={2} />, <PeopleIcon key={3} />];

const icons = {
  Clouds: 0,
  BusinessUnits: 1,
  Owners: 2
};

const messageId = text("messageId", "cloud");

const iconIndex = select("icon", icons, 0);

export const basic = () => <ButtonSwitch buttons={buttons} />;

export const withLabelsAndIcons = () => <ButtonSwitch buttons={[{ messageId, icon: iconsArray[iconIndex], link: "/" }]} />;

export const withButtons = () => <ButtonSwitch buttons={buttons.slice(0, select("Count", { 1: 1, 2: 2, 3: 3 }, "1"))} />;
