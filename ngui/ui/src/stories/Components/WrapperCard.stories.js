import React from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import WrapperCard from "components/WrapperCard";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/WrapperCard`,
  argTypes: {
    link: { name: "Link", control: "text", defaultValue: "/test" },
    href: { name: "Href", control: "text", defaultValue: "https://hystax.com/" }
  }
};

export const basic = () => <WrapperCard title="Optscale" buttonText="Go to OptScale" />;

export const withText = () => (
  <WrapperCard title="Optscale" button={{ show: true, messageId: "goToDashboard" }}>
    Some text
  </WrapperCard>
);

export const withInternalLink = (args) => (
  <WrapperCard
    title="Optscale"
    button={{
      show: true,
      messageId: "goToDashboard",
      link: args.link
    }}
  >
    Some text
  </WrapperCard>
);

export const withExternalLink = (args) => (
  <WrapperCard
    title="Optscale"
    button={{
      show: true,
      messageId: "buy",
      href: args.href
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
