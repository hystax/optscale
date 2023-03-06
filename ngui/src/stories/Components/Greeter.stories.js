import React from "react";
import Greeter from "components/Greeter";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Greeter`
};

export const basic = () => <Greeter form={<div>Form</div>} />;
