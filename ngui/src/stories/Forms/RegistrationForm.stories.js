import React from "react";
import { boolean, text } from "@storybook/addon-knobs";
import RegistrationForm from "components/RegistrationForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/RegistrationForm`
};

export const basic = () => (
  <RegistrationForm
    isLoading={boolean("isLoading", false)}
    onSubmit={() => console.log("submit")}
    sendState={text("sendState(success, error, unknown)", "unknown")}
  />
);
