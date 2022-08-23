import React from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import { text } from "@storybook/addon-knobs";
import WrapperCard from "components/WrapperCard";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/WrapperCard`
};

export const basic = () => <WrapperCard title="Tasks" buttonText="Go to Tasks" />;

export const withText = () => (
  <WrapperCard title="Tasks" button={{ show: true, messageId: "goToTasks" }}>
    Some text
  </WrapperCard>
);

export const withInternalLink = () => (
  <WrapperCard
    title="Tasks"
    button={{
      show: true,
      messageId: "goToTasks",
      link: text("link", "/test")
    }}
  >
    Some text
  </WrapperCard>
);

export const withExternalLink = () => (
  <WrapperCard
    title="Optscale"
    button={{
      show: true,
      messageId: "buy",
      href: text("href", "https://hystax.com/")
    }}
  >
    Some text
  </WrapperCard>
);

export const withTitleButton = () => (
  <WrapperCard
    title="Optscale"
    titleButton={{
      type: "button",
      tooltip: {
        title: "Button tooltip"
      },
      buttonProps: {
        messageId: "add"
      }
    }}
  >
    Some text
  </WrapperCard>
);

export const withTitleIconButton = () => (
  <WrapperCard
    title="Optscale"
    titleButton={{
      type: "icon",
      tooltip: {
        title: "Button tooltip"
      },
      buttonProps: {
        icon: <ListAltOutlinedIcon />
      }
    }}
  >
    Some text
  </WrapperCard>
);
