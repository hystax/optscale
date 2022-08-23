import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import "regenerator-runtime/runtime";
import App from "./App";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        mainMenuItems: [],
        auth: {},
        routes: {},
        api: { latestErrorLabel: "" }
      }}
    >
      <App />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
