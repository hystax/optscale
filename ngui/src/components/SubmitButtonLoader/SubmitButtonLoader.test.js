import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SubmitButtonLoader from "./SubmitButtonLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SubmitButtonLoader isLoading messageId="name" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
