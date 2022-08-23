import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Accordion from "./Accordion";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Accordion>
        <div>Summary</div>
        <div>Details</div>
      </Accordion>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
