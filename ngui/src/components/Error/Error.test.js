import React from "react";
import ReactDOM from "react-dom";
import Error from "components/Error";
import TestProvider from "tests/TestProvider";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Error messageId="notFound" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
