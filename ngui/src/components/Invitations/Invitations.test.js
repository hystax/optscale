import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Invitations from "./Invitations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Invitations invitations={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
