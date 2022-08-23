import React from "react";
import ArrowForwardOutlinedIcon from "@mui/icons-material/ArrowForwardOutlined";
import SummaryCard from "components/SummaryCard";
import { select, text, boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/SummaryCard`
};

export const basic = () => <SummaryCard value="$123456.321" caption="This is some caption" />;

export const withHelp = () => (
  <SummaryCard value="$123456.321" caption="This is some caption" help={{ show: true, messageId: "hystax" }} />
);

export const withKnobs = () => (
  <SummaryCard
    value={text("value", "$123456.321")}
    caption={text("caption", "This is some caption")}
    color={select("color", ["primary", "secondary", "success", "error", "warning"], "primary")}
    help={{ show: boolean("show help", true), messageId: "hystax" }}
    button={{ show: boolean("show button", true), icon: <ArrowForwardOutlinedIcon /> }}
  />
);

export const withButton = () => (
  <SummaryCard
    value="$123456.321"
    caption="This is some caption"
    button={{ show: true, icon: <ArrowForwardOutlinedIcon />, tooltip: { show: true, messageId: "add" } }}
  />
);
