import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PanelLoader from "./PanelLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PanelLoader />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
