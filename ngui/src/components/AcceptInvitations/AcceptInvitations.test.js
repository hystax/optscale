import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AcceptInvitations from "./AcceptInvitations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AcceptInvitations activateScope={() => {}} />{" "}
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
