import React from "react";
import { text, boolean } from "@storybook/addon-knobs";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import InputAdornment from "@mui/material/InputAdornment";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Input`
};

export const basic = () => <Input />;

export const withHelp = () => (
  <Input
    InputProps={{
      endAdornment: (
        <InputAdornment position="end">
          <QuestionMark messageId="hystax" />
        </InputAdornment>
      )
    }}
    label={"Label"}
  />
);

export const withKnobs = () => <Input label={text("label", "Label")} isMasked={boolean("isMasked", false)} />;
