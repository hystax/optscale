import React from "react";
import ConnectCloudAccountForm from "components/ConnectCloudAccountForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/ConnectCloudAccountForm`
};

export const basic = () => (
  <ConnectCloudAccountForm organizationId="test" onSubmit={() => {}} isLoading={false} sendState="test" />
);
