import React from "react";
import ReactDOM from "react-dom";
import selectorsMock from "mocks/selectorsMock";
import TestProvider from "tests/TestProvider";
import Selector from "./Selector";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Selector data={selectorsMock} labelId="organization" onChange={() => {}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
