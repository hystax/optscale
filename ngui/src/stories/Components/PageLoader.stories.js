import React from "react";
import PageLoader from "components/PageLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/PageLoader`
};

export const basic = () => <PageLoader />;
