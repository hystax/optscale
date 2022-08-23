import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Redirector from "./Redirector";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Redirector condition={1 > 0} to={"/"}>
        <div>test</div>
      </Redirector>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
