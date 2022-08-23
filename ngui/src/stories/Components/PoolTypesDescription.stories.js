import React from "react";
import PoolTypesDescription from "components/PoolTypesDescription";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/PoolTypesDescription`
};

export const basic = () => <PoolTypesDescription />;
