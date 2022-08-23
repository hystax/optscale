import React from "react";
import { boolean } from "@storybook/addon-knobs";
import CreateClusterTypeForm from "components/CreateClusterTypeForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/CreateClusterTypeForm`
};

export const basic = () => (
  <CreateClusterTypeForm
    onSubmit={() => console.log("On submit")}
    onCancel={() => console.log("On submit")}
    isSubmitLoading={boolean("isSubmitLoading", false)}
  />
);
