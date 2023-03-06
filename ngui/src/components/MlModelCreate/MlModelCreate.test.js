import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlModelCreate from "./MlModelCreate";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlModelCreate />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
