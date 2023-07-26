import React from "react";
import { ClusterTypesMocked } from "components/ClusterTypes";
import { KINDS } from "stories";

export default {
  title: `${KINDS.MOCKUPS}/ClusterTypesMocked`
};

export const basic = () => <ClusterTypesMocked />;
