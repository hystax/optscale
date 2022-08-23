import React from "react";
import { ClusterTypesMocked } from "components/ClusterTypes";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/ClusterTypes`
};

export const basic = () => <ClusterTypesMocked />;
