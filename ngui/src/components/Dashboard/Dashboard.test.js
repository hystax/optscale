import React from "react";
import ReactDOM from "react-dom";
import { PRODUCT_TOUR } from "components/ProductTour";
import TestProvider from "tests/TestProvider";
import Dashboard from "./Dashboard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        [PRODUCT_TOUR]: { isOpen: false, isFinished: false }
      }}
    >
      <Dashboard />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
