import React from "react";
import ResetPassword from "components/ResetPassword";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/ResetPassword`,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => (
  <ResetPassword isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState="SUCCESS" />
);
