import Typography from "@mui/material/Typography";
import Accordion from "components/Accordion";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Accordion`,
  argTypes: {
    disableExpandedSpacing: { name: "Disable expanded spacing", control: "boolean", defaultValue: false },
    zeroSummaryMinHeight: { name: "Zero summary min height", control: "boolean", defaultValue: false },
    hideExpandIcon: { name: "Hide expand icon", control: "boolean", defaultValue: false },
    summary: { name: "Summary", control: "text", defaultValue: "Accordion summary" },
    details: { name: "Details", control: "text", defaultValue: "Accordion details" }
  }
};

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
