import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AcceptInvitation from "./AcceptInvitation";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AcceptInvitation invitation={{}} onAccept={() => {}} onDecline={() => {}} isUpdateLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
