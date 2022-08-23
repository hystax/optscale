import React from "react";
import { CloudAccountsOverviewMocked } from "components/CloudAccountsOverview";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/CloudAccountsOverview`
};

export const basic = () => <CloudAccountsOverviewMocked />;
