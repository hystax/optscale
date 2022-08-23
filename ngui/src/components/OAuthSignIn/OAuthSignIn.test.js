import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OAuthSignIn from "./OAuthSignIn";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OAuthSignIn />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
