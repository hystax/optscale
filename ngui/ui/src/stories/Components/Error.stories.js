import React from "react";
import Error from "components/Error";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Error`
};

export const basic = () => <Error messageId="Not found" />;
