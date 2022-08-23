import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import WrongInvitationEmailAlert from "./WrongInvitationEmailAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <WrongInvitationEmailAlert />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
