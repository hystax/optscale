import React from "react";
import SomethingWentWrong from "components/SomethingWentWrong";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/SomethingWentWrong`
};

export const basic = () => <SomethingWentWrong />;
