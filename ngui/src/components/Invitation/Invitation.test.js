import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Invitation from "./Invitation";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Invitation
        owner={{ name: "name", email: "email" }}
        organizationNameInvitedTo="organizationNameInvitedTo"
        invitesToOrganization={[]}
        invitesToPools={[]}
      />
    </TestProvider>
  );
  root.unmount();
});
