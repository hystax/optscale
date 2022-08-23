import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AnomaliesFilters from "./AnomaliesFilters";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AnomaliesFilters filters={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
