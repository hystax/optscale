import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationDescription from "./RecommendationDescription";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationDescription messageId="inactiveConsoleUsersDescription" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
