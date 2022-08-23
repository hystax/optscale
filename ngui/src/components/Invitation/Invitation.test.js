import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Invitation from "./Invitation";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Invitation
        owner={{ name: "name", email: "email" }}
        organizationNameInvitedTo="organizationNameInvitedTo"
        invitesToOrganization={[]}
        invitesToPools={[]}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
