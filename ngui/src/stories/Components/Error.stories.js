import React from "react";
import Error from "components/Error";
import { select } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Error`
};

const messages = {
  "Not found": "notFound",
  Forbidden: "forbidden"
};

export const withKnobs = () => <Error messageId={select("message", messages, "Not found")} />;
