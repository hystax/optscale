import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import JsonView from "./JsonView";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <JsonView value={{}} onChange={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
