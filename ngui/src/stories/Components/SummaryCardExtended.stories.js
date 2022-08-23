import React from "react";
import ArrowForwardOutlinedIcon from "@mui/icons-material/ArrowForwardOutlined";
import SummaryCardExtended from "components/SummaryCardExtended";
import { select, text, boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/SummaryCardExtended`
};

export const withKnobs = () => (
  <SummaryCardExtended
    value={text("value", "$123456.321")}
    color={select("color", ["primary", "secondary", "success", "error", "warning"], "primary")}
    caption={text("caption", "This is some caption")}
    help={{ show: boolean("show help", true), messageId: "hystax" }}
    relativeValue={text("relative value", "%15")}
    relativeValueCaption={text("relative value caption", "This is some relative caption")}
    button={{ show: boolean("show button", true), icon: <ArrowForwardOutlinedIcon /> }}
  />
);
