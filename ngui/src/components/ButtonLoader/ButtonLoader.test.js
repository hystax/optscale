import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ButtonLoader from "./ButtonLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const testAction = () => {
    console.log("test");
  };
  ReactDOM.render(
    <TestProvider>
      <ButtonLoader messageId="checkConnection" onClick={testAction} isLoading={false} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
