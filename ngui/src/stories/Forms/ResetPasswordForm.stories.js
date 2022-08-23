import React from "react";
import { boolean, text } from "@storybook/addon-knobs";
import ResetPasswordForm from "components/ResetPasswordForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/ResetPasswordForm`
};

export const basic = () => (
  <ResetPasswordForm
    isLoading={boolean("isLoading", false)}
    onSubmit={() => console.log("submit")}
    sendState={text("sendState(success, error, unknown)", "success")}
  />
);
