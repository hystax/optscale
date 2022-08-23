import React from "react";
import { boolean } from "@storybook/addon-knobs";
import ResetPassword from "components/ResetPassword";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/ResetPassword`
};

export const basic = () => (
  <ResetPassword isLoading={boolean("isLoading", false)} onSubmit={() => console.log("submit")} sendState="SUCCESS" />
);
