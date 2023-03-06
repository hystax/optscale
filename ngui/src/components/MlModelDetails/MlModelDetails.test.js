import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlModelDetails from "./MlModelDetails";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlModelDetails application={{}} isLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
