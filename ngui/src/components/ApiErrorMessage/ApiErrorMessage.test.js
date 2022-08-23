import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ApiErrorMessage from "./ApiErrorMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ApiErrorMessage errorCode="OEXXX" reason="reason" url="https://" params={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
