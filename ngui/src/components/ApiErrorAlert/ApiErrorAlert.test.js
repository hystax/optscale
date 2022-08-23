import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ApiErrorAlert from "./ApiErrorAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        api: { latestErrorLabel: "" }
      }}
    >
      <ApiErrorAlert />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
