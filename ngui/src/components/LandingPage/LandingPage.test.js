import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import LandingPage from "./LandingPage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LandingPage titleMessageId="hystax" featureMessageId="hystax" featureActionMessageId="hystax" featureUrl="https://" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
