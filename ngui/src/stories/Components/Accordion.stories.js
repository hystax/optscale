import React from "react";
import Typography from "@mui/material/Typography";
import { text, boolean } from "@storybook/addon-knobs";
import Accordion from "components/Accordion";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Accordion`
};

export const withKnobs = () => (
  <>
    {[...Array(3).keys()].map((key) => (
      <Accordion
        key={key}
        disableExpandedSpacing={boolean("disableExpandedSpacing", false)}
        zeroSummaryMinHeight={boolean("zeroSummaryMinHeight", false)}
        hideExpandIcon={boolean("hideExpandIcon", false)}
      >
        <Typography>{text(`summary ${key}`, `Accordion summary ${key}`)}</Typography>
        <Typography>{text(`details ${key}`, `Accordion details ${key}`)}</Typography>
      </Accordion>
    ))}
  </>
);
