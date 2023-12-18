import Typography from "@mui/material/Typography";
import type { Meta } from "@storybook/react";
import Accordion from "components/Accordion";

const meta: Meta = {
  component: Accordion,
  argTypes: {
    disableExpandedSpacing: { label: "Disable expanded spacing", control: "boolean", defaultValue: true },
    zeroSummaryMinHeight: { name: "Zero summary min height", control: "boolean", defaultValue: false },
    hideExpandIcon: { name: "Hide expand icon", control: "boolean", defaultValue: false },
    summary: { name: "Summary", control: "text", defaultValue: "Accordion summary" },
    details: { name: "Details", control: "text", defaultValue: "Accordion details" }
  }
};

export default meta;

export const withKnobs = (args) => (
  <>
    {[...Array(3).keys()].map((key) => (
      <Accordion
        key={key}
        disableExpandedSpacing={args.disableExpandedSpacing}
        zeroSummaryMinHeight={args.zeroSummaryMinHeight}
        hideExpandIcon={args.hideExpandIcon}
      >
        <Typography>{`${args.summary} ${key}`}</Typography>
        <Typography>{`${args.details} ${key}`}</Typography>
      </Accordion>
    ))}
  </>
);
