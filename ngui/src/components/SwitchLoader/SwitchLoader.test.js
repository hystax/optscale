import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SwitchLoader from "./SwitchLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SwitchLoader />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
